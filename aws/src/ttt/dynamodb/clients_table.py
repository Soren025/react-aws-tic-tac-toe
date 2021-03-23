import os

from . import dynamodb


class AttributeNames:
    CONNECTION_ID = 'connection_id'
    ROOM_NAME = 'room_name'


table = dynamodb.Table(os.getenv('CLIENTS_TABLE_NAME'))


def generate_key(connection_id):
    return {
        AttributeNames.CONNECTION_ID: connection_id
    }


def add(connection_id):
    table.put_item(
        Item={
            AttributeNames.CONNECTION_ID: connection_id,
        },
        ReturnValues='NONE',
    )


def remove(connection_id):
    response = table.delete_item(
        Key=generate_key(connection_id),
        ReturnValues='ALL_OLD',
    )

    return response.get('Attributes', {}).get(AttributeNames.ROOM_NAME)


def set_room(connection_id, room_name):
    response = table.update_item(
        Key=generate_key(connection_id),
        ExpressionAttributeNames={
            '#room_name': AttributeNames.ROOM_NAME,
        },
        ExpressionAttributeValues={
            ':room_name': room_name,
        },
        UpdateExpression='SET #room_name = :room_name',
        ReturnValues='UPDATED_OLD',
    )

    return response.get('Attributes', {}).get(AttributeNames.ROOM_NAME)


def get_room(connection_id):
    response = table.get_item(
        Key=generate_key(connection_id),
        ConsistentRead=True,
        ExpressionAttributeNames={
            '#room_name': AttributeNames.ROOM_NAME,
        },
        ProjectionExpression='#room_name'
    )

    return response.get('Item', {}).get(AttributeNames.ROOM_NAME)


def clear_room(connection_id):
    response = table.update_item(
        Key=generate_key(connection_id),
        ExpressionAttributeNames={
            '#room_name': AttributeNames.ROOM_NAME,
        },
        UpdateExpression='REMOVE #room_name',
        ReturnValues='UPDATED_OLD',
    )

    return response.get('Item', {}).get(AttributeNames.ROOM_NAME)
