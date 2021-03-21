import os

from . import dynamodb


class AttributeNames:
    CONNECTION_ID = 'connection_id'
    READY = 'ready'
    ROOM_NAME = 'room_name'
    SYMBOL = 'symbol'


table = dynamodb.Table(os.getenv('CLIENTS_TABLE_NAME'))


def generate_key(connection_id):
    return {
        AttributeNames.CONNECTION_ID: connection_id
    }


def add(connection_id):
    table.put_item(
        Item={
            AttributeNames.CONNECTION_ID: connection_id,
            AttributeNames.READY: False,
        },
        ReturnValues='NONE',
    )


def remove(connection_id):
    table.delete_item(
        Key=generate_key(connection_id),
    )


def set_room(connection_id, room_name, symbol):
    table.update_item(
        Key=generate_key(connection_id),
        ExpressionAttributeNames={
            '#room_name': AttributeNames.ROOM_NAME,
            '#symbol': AttributeNames.SYMBOL,
        },
        ExpressionAttributeValues={
            ':room_name': room_name,
            ':symbol': symbol,
        },
        UpdateExpression='SET #room_name = :room_name, #symbol = :symbol',
        ReturnValues='NONE',
    )


def clear_room(connection_id):
    table.update_item(
        Key=generate_key(connection_id),
        ExpressionAttributeNames={
            '#room_name': AttributeNames.ROOM_NAME,
            '#symbol': AttributeNames.SYMBOL,
        },
        UpdateExpression='REMOVE #room_name, #symbol',
        ReturnValues='NONE',
    )
