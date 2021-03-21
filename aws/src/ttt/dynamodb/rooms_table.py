import os

from botocore.exceptions import ClientError

from ttt import game

from . import dynamodb


class AttributeNames:
    ROOM_NAME = 'room_name'
    CLIENTS = 'clients'
    HISTORY = 'history'
    STEP_NUMBER = 'step_number'
    X_IS_NEXT = 'x_is_next'


table = dynamodb.Table(os.getenv('ROOMS_TABLE_NAME'))


def generate_key(room_name):
    return {
        AttributeNames.ROOM_NAME: room_name
    }


def join_room(room_name, connection_id):
    if join_room_as(room_name, connection_id, game.Symbols.X_VALUE):
        return game.Symbols.X_VALUE
    elif join_room_as(room_name, connection_id, game.Symbols.O_VALUE):
        return game.Symbols.O_VALUE
    else:
        return None


def join_room_as(room_name, connection_id, symbol):
    try:
        table.update_item(
            Key=generate_key(room_name),
            ExpressionAttributeNames={
                '#symbol': symbol,
                '#clients': AttributeNames.CLIENTS,
            },
            ExpressionAttributeValues={
                ':connection_id': connection_id,
                ':client': {connection_id},
            },
            UpdateExpression='SET #symbol = :connection_id ADD #clients :client',
            ConditionExpression='attribute_not_exists(#symbol) AND (NOT contains(#clients, :connection_id))',
            ReturnValues='NONE',
        )
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return False
        else:
            raise


def get_clients(room_name):
    response = table.get_item(
        Key=generate_key(room_name),
        ConsistentRead=True,
        ExpressionAttributeNames={
            '#clients': AttributeNames.CLIENTS,
        },
        ProjectionExpression='#clients',
    )

    return response.get('Item', {}).get(AttributeNames.CLIENTS, set())


def get_other_client(room_name, symbol):
    other_symbol = game.get_other_symbol(symbol)
    if other_symbol is None:
        return None

    response = table.get_item(
        Key=generate_key(room_name),
        ConsistentRead=True,
        ExpressionAttributeNames={
            '#symbol': other_symbol,
        },
        ProjectionExpression='#symbol',
    )

    return response.get('Item', {}).get(other_symbol)


def clear_symbol(room_name, symbol, connection_id):
    try:
        response = table.update_item(
            Key=generate_key(room_name),
            ExpressionAttributeNames={
                '#symbol': symbol,
                '#clients': AttributeNames.CLIENTS,
                '#history': AttributeNames.HISTORY,
                '#step_number': AttributeNames.STEP_NUMBER,
                '#x_is_next': AttributeNames.X_IS_NEXT,
            },
            ExpressionAttributeValues={
                ':connection_id': connection_id,
                ':client': {connection_id}
            },
            UpdateExpression='REMOVE #symbol, #history, #step_number, #x_is_next DELETE #clients :client',
            ConditionExpression='#symbol = :connection_id',
            ReturnValues='ALL_NEW',
        )

        other_client = response['Attributes'].get(game.get_other_symbol(symbol))
        if other_client is None:
            remove(room_name)

        return other_client
    except ClientError as e:
        if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
            raise


def remove(room_name):
    table.delete_item(
        Key=generate_key(room_name),
        ReturnValues='NONE',
    )
