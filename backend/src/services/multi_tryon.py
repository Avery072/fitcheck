"""
Multi-Step Virtual Try-On System

This system processes multiple clothing items sequentially, creating individual
virtual try-on images for each item using the same person photo.

Features:
- Sequential Bedrock Nova Canvas calls
- Progress tracking
- Result aggregation
- Error handling and recovery
- Batch processing
"""

import json
import time
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

from utils.s3 import get_from_s3, upload_to_s3, generate_presigned_get_url
from utils.dynamodb import put_item, get_item


class MultiTryOnProcessor:
    """Handles multi-step virtual try-on processing"""
    
    def __init__(self, user_sub: str):
        self.user_sub = user_sub
        self.bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
        
    def process_multiple_items(
        self, 
        items: List[Dict[str, Any]], 
        body_asset_key: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process multiple clothing items for virtual try-on
        
        Args:
            items: List of clothing items to try on
            body_asset_key: S3 key for user's body photo
            session_id: Optional session ID for tracking
            
        Returns:
            Dict with results, progress, and metadata
        """
        
        if not session_id:
            session_id = f"multi-tryon-{uuid.uuid4().hex[:12]}"
            
        print(f"🎯 Starting multi-step try-on session: {session_id}")
        print(f"📦 Processing {len(items)} items for user: {self.user_sub}")
        
        # Initialize session tracking
        session_data = {
            'session_id': session_id,
            'user_sub': self.user_sub,
            'total_items': len(items),
            'processed_items': 0,
            'status': 'processing',
            'started_at': datetime.utcnow().isoformat(),
            'results': [],
            'errors': []
        }
        
        # Save initial session state
        self._save_session_state(session_data)
        
        try:
            # Get user's body photo once
            print(f"📸 Loading body photo: {body_asset_key}")
            body_image_bytes = get_from_s3(body_asset_key)
            body_image_base64 = self._load_image_bytes_as_base64(body_image_bytes)
            
            # Process each item sequentially
            for i, item in enumerate(items):
                print(f"👕 Processing item {i+1}/{len(items)}: {item.get('title', 'Unknown')}")
                
                try:
                    result = self._process_single_item(
                        item=item,
                        body_image_base64=body_image_base64,
                        session_id=session_id,
                        item_index=i
                    )
                    
                    session_data['results'].append(result)
                    session_data['processed_items'] += 1
                    
                    # Update progress
                    self._save_session_state(session_data)
                    
                    print(f"✅ Item {i+1} processed successfully")
                    
                except Exception as e:
                    error_msg = f"Failed to process item {i+1}: {str(e)}"
                    print(f"❌ {error_msg}")
                    
                    error_result = {
                        'item_index': i,
                        'item_title': item.get('title', 'Unknown'),
                        'error': str(e),
                        'status': 'failed'
                    }
                    
                    session_data['errors'].append(error_result)
                    session_data['processed_items'] += 1
                    
                    # Continue with next item
                    continue
            
            # Mark session as completed
            session_data['status'] = 'completed'
            session_data['completed_at'] = datetime.utcnow().isoformat()
            self._save_session_state(session_data)
            
            print(f"🎉 Multi-step try-on completed! Processed {session_data['processed_items']}/{session_data['total_items']} items")
            
            return {
                'session_id': session_id,
                'status': 'completed',
                'total_items': session_data['total_items'],
                'processed_items': session_data['processed_items'],
                'successful_items': len(session_data['results']),
                'failed_items': len(session_data['errors']),
                'results': session_data['results'],
                'errors': session_data['errors'],
                'summary_url': self._generate_summary_url(session_id)
            }
            
        except Exception as e:
            print(f"💥 Multi-step try-on failed: {str(e)}")
            session_data['status'] = 'failed'
            session_data['error'] = str(e)
            self._save_session_state(session_data)
            
            return {
                'session_id': session_id,
                'status': 'failed',
                'error': str(e),
                'results': session_data['results'],
                'errors': session_data['errors']
            }
    
    def _process_single_item(
        self, 
        item: Dict[str, Any], 
        body_image_base64: str,
        session_id: str,
        item_index: int
    ) -> Dict[str, Any]:
        """Process a single clothing item"""
        
        # Generate unique render key for this item
        render_key = f'fit-renders/{self.user_sub}/{session_id}/item-{item_index:03d}.png'
        
        # Get garment image
        garment_image_bytes = self._fetch_image_from_url(item['imageUrl'])
        garment_image_base64 = self._load_image_bytes_as_base64(garment_image_bytes)
        
        # Determine garment class
        category = item.get('category', '').lower()
        garment_class = self._determine_garment_class(category)
        
        print(f"🎨 Generating try-on for {item.get('title')} (class: {garment_class})")
        
        # Prepare Bedrock request
        inference_params = {
            "taskType": "VIRTUAL_TRY_ON",
            "virtualTryOnParams": {
                "sourceImage": body_image_base64,
                "referenceImage": garment_image_base64,
                "maskType": "GARMENT",
                "garmentBasedMask": {
                    "garmentClass": garment_class
                }
            }
        }
        
        # Call Bedrock Nova Canvas
        response = self.bedrock.invoke_model(
            body=json.dumps(inference_params),
            modelId="amazon.nova-canvas-v1:0",
            accept="application/json",
            contentType="application/json"
        )
        
        # Parse response
        response_json = json.loads(response["body"].read())
        images = response_json.get("images", [])
        
        if not images:
            raise Exception("Bedrock returned no images")
        
        # Get first generated image
        image_base64 = images[0]
        image_bytes = self._decode_base64_image(image_base64)
        
        # Upload to S3
        upload_to_s3(render_key, image_bytes, 'image/png')
        
        # Generate presigned URL for easy access
        image_url = generate_presigned_get_url(render_key, expiration=3600)
        
        return {
            'item_index': item_index,
            'item_title': item.get('title', 'Unknown'),
            'item_retailer': item.get('retailer', 'unknown'),
            'item_category': item.get('category', 'unknown'),
            'garment_class': garment_class,
            'render_key': render_key,
            'image_url': image_url,
            'status': 'success',
            'processed_at': datetime.utcnow().isoformat()
        }
    
    def _determine_garment_class(self, category: str) -> str:
        """Determine Bedrock garment class from category"""
        if 'pant' in category or 'jean' in category or 'short' in category:
            return "LOWER_BODY"
        elif 'dress' in category or 'jumpsuit' in category:
            return "FULL_BODY"
        else:
            return "UPPER_BODY"
    
    def _load_image_bytes_as_base64(self, image_bytes: bytes) -> str:
        """Convert image bytes to base64 string"""
        import base64
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def _decode_base64_image(self, image_base64: str) -> bytes:
        """Decode base64 image to bytes"""
        import base64
        return base64.b64decode(image_base64)
    
    def _fetch_image_from_url(self, url: str) -> bytes:
        """Fetch image from URL"""
        import requests
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content
    
    def _save_session_state(self, session_data: Dict[str, Any]) -> None:
        """Save session state to DynamoDB"""
        try:
            session_key = f"MULTI_TRYON_SESSION#{session_data['session_id']}"
            item = {
                'pk': f"USER#{self.user_sub}",
                'sk': session_key,
                'session_data': session_data,
                'updated_at': datetime.utcnow().isoformat()
            }
            put_item(item)
        except Exception as e:
            print(f"⚠️ Failed to save session state: {e}")
    
    def _generate_summary_url(self, session_id: str) -> str:
        """Generate URL for viewing all results"""
        return f"/multi-tryon-results/{session_id}"
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a multi-step session"""
        try:
            session_key = f"MULTI_TRYON_SESSION#{session_id}"
            item = get_item(f"USER#{self.user_sub}", session_key)
            
            if item and 'session_data' in item:
                return item['session_data']
            return None
        except Exception as e:
            print(f"⚠️ Failed to get session status: {e}")
            return None


def process_multi_tryon(
    user_sub: str,
    items: List[Dict[str, Any]],
    body_asset_key: str,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main function for processing multiple items
    
    Args:
        user_sub: User's Cognito sub ID
        items: List of clothing items
        body_asset_key: S3 key for user's body photo
        session_id: Optional session ID
        
    Returns:
        Dict with processing results
    """
    
    processor = MultiTryOnProcessor(user_sub)
    return processor.process_multiple_items(items, body_asset_key, session_id)


def get_multi_tryon_status(user_sub: str, session_id: str) -> Optional[Dict[str, Any]]:
    """Get status of a multi-step try-on session"""
    processor = MultiTryOnProcessor(user_sub)
    return processor.get_session_status(session_id)
