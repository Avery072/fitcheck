import json
import base64
import io
from datetime import datetime
from utils.s3 import upload_to_s3, get_from_s3
import requests
import boto3
from PIL import Image


def load_image_as_base64(path):
    """Load image file and convert to base64 string"""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def load_image_bytes_as_base64(image_bytes):
    """Convert image bytes to base64 string"""
    return base64.b64encode(image_bytes).decode("utf-8")


def generate_mvp_composite(
    user_sub: str,
    fit_id: str,
    items: list,
    body_asset_key: str = None
) -> str:
    """
    MVP Compositor - Simple image collage (no AI)

    Creates a grid of product images as a simple visualization.
    For real virtual try-on, use generate_bedrock_tryon() instead.

    Args:
        user_sub: User's Cognito sub ID
        fit_id: Unique fit ID
        items: List of items to composite (each has 'imageUrl')
        body_asset_key: S3 key for user's body image (not used in MVP)

    Returns:
        S3 key for the rendered composite image
    """
    from PIL import Image, ImageDraw, ImageFont

    render_key = f'fit-renders/{user_sub}/{fit_id}.png'

    # Download product images
    product_images = []
    for item in items[:4]:  # Limit to 4 items max
        try:
            img_bytes = fetch_image_from_url(item['imageUrl'])
            img = Image.open(io.BytesIO(img_bytes))
            product_images.append(img)
        except Exception as e:
            print(f"Failed to load image {item['imageUrl']}: {e}")

    if not product_images:
        # No images loaded - create placeholder
        img = Image.new('RGB', (400, 400), color='#3B82F6')
        draw = ImageDraw.Draw(img)
        draw.text((150, 180), "No Items", fill='white')
    else:
        # Create a grid of images
        img_size = 200
        cols = 2
        rows = (len(product_images) + 1) // 2

        canvas = Image.new('RGB', (img_size * cols, img_size * rows), color='white')

        for idx, product_img in enumerate(product_images):
            # Resize to fit grid
            product_img.thumbnail((img_size, img_size))

            # Calculate position
            x = (idx % cols) * img_size
            y = (idx // cols) * img_size

            # Paste onto canvas
            canvas.paste(product_img, (x, y))

        img = canvas

    # Save to bytes buffer
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    # Upload to S3
    upload_to_s3(render_key, buffer.read(), 'image/png')

    return render_key


def generate_bedrock_tryon(
    user_sub: str,
    fit_id: str,
    items: list,
    body_asset_key: str = None
) -> str:
    """
    Bedrock Nova Canvas - Real Virtual Try-On

    Uses Amazon Bedrock Nova Canvas to create realistic virtual try-on images.

    Args:
        user_sub: User's Cognito sub ID
        fit_id: Unique fit ID
        items: List of items to try on (uses first item for now)
        body_asset_key: S3 key for user's body/person photo (required!)

    Returns:
        S3 key for the generated virtual try-on image
    """

    if not body_asset_key:
        raise ValueError("body_asset_key is required for Bedrock virtual try-on")

    if not items or len(items) == 0:
        raise ValueError("At least one item is required for virtual try-on")

    render_key = f'fit-renders/{user_sub}/{fit_id}.png'

    # Step 1: Get user's body photo from S3
    print(f"Fetching body image from S3: {body_asset_key}")
    body_image_bytes = get_from_s3(body_asset_key)
    body_image_base64 = load_image_bytes_as_base64(body_image_bytes)

    # Step 2: Get first garment image from URL
    garment_item = items[0]  # For now, just use first item
    print(f"Fetching garment image from: {garment_item['imageUrl']}")
    garment_image_bytes = fetch_image_from_url(garment_item['imageUrl'])
    garment_image_base64 = load_image_bytes_as_base64(garment_image_bytes)

    # Step 3: Determine garment class from category
    category = garment_item.get('category', '').lower()
    if 'pant' in category or 'jean' in category or 'short' in category:
        garment_class = "LOWER_BODY"
    elif 'dress' in category or 'jumpsuit' in category:
        garment_class = "FULL_BODY"
    else:
        # Default to upper body (shirts, jackets, hoodies, etc.)
        garment_class = "UPPER_BODY"

    print(f"Using garment class: {garment_class}")

    # Step 4: Prepare Bedrock request
    inference_params = {
        "taskType": "VIRTUAL_TRY_ON",
        "virtualTryOnParams": {
            "sourceImage": body_image_base64,      # Person photo
            "referenceImage": garment_image_base64, # Garment photo
            "maskType": "GARMENT",                  # Focus on garment area
            "garmentBasedMask": {
                "garmentClass": garment_class       # UPPER_BODY, LOWER_BODY, or FULL_BODY
            }
        }
    }

    # Step 5: Create Bedrock runtime client
    bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

    # Step 6: Invoke Bedrock Nova Canvas
    print("Invoking Bedrock Nova Canvas...")
    response = bedrock.invoke_model(
        body=json.dumps(inference_params),
        modelId="amazon.nova-canvas-v1:0",
        accept="application/json",
        contentType="application/json"
    )

    # Step 7: Parse response
    response_json = json.loads(response["body"].read())
    images = response_json.get("images", [])

    if not images:
        raise Exception("Bedrock returned no images")

    # Step 8: Get first generated image
    image_base64 = images[0]
    image_bytes = base64.b64decode(image_base64)

    # Step 9: Save to S3
    print(f"Uploading result to S3: {render_key}")
    upload_to_s3(render_key, image_bytes, 'image/png')

    print(f"✅ Virtual try-on completed! Saved to {render_key}")

    return render_key


def fetch_image_from_s3(key: str) -> bytes:
    """Helper to fetch image from S3."""
    return get_from_s3(key)


def fetch_image_from_url(url: str) -> bytes:
    """Helper to fetch image from URL."""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.content
