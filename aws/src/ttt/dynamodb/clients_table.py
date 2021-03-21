import os

from . import dynamodb


class AttributeNames:
    CONNECTION_ID = 'connection_id'
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
        },
        ReturnValues='NONE',
    )


def remove(connection_id):
    response = table.delete_item(
        Key=generate_key(connection_id),
        ReturnValues='ALL_OLD',
    )

    attributes = response['Attributes']
    if AttributeNames.ROOM_NAME in attributes:
        return {
            AttributeNames.ROOM_NAME: attributes[AttributeNames.ROOM_NAME],
            AttributeNames.SYMBOL: attributes[AttributeNames.SYMBOL],
        }
    else:
        return None


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
