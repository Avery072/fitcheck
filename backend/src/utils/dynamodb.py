import os
import boto3
from typing import Dict, List, Any, Optional

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('TABLE_NAME', 'fitcheck-data-dev')
table = dynamodb.Table(TABLE_NAME)


def put_item(item: Dict[str, Any]) -> None:
    """Put an item into DynamoDB."""
    table.put_item(Item=item)


def get_item(pk: str, sk: str) -> Optional[Dict[str, Any]]:
    """Get an item from DynamoDB."""
    response = table.get_item(Key={'pk': pk, 'sk': sk})
    return response.get('Item')


def query_items(pk: str, sk_prefix: Optional[str] = None) -> List[Dict[str, Any]]:
    """Query items from DynamoDB."""
    if sk_prefix:
        response = table.query(
            KeyConditionExpression='pk = :pk AND begins_with(sk, :sk)',
            ExpressionAttributeValues={':pk': pk, ':sk': sk_prefix}
        )
    else:
        response = table.query(
            KeyConditionExpression='pk = :pk',
            ExpressionAttributeValues={':pk': pk}
        )
    return response.get('Items', [])


def delete_item(pk: str, sk: str) -> None:
    """Delete an item from DynamoDB."""
    table.delete_item(Key={'pk': pk, 'sk': sk})
