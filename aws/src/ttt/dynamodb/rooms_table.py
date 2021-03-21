import os

from botocore.exceptions import ClientError

from ttt import game

from . import dynamodb


class AttributeNames:
    ROOM_NAME = 'room_name'
    CONNECTION_IDS = 'connection_ids'
    STATE = 'state'


class ClientAttributeNames:
    CONNECTION_ID = 'connection_id'
    READY = 'ready'


class StateAttributeNames:
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
                '#connection_ids': AttributeNames.CONNECTION_IDS,
            },
            ExpressionAttributeValues={
                ':connection_id': connection_id,
                ':connection_id_set': {connection_id},
                ':client': {
                    ClientAttributeNames.CONNECTION_ID: connection_id,
                    ClientAttributeNames.READY: False,
                }
            },
            UpdateExpression='SET #symbol = :client ADD #connection_ids :connection_id_set',
            ConditionExpression='attribute_not_exists(#symbol) AND (NOT contains(#connection_ids, :connection_id))',
            ReturnValues='NONE',
        )
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return False
        else:
            raise


def get_client(room_name, symbol):
    response = table.get_item(
        Key=generate_key(room_name),
        ConsistentRead=True,
        ExpressionAttributeNames={
            '#symbol': game.Symbols.X_VALUE,
        },
        ProjectionExpression='#symbol',
    )

    return response.get('Item', {}).get(symbol)


def get_other_client(room_name, symbol):
    return get_client(room_name, game.get_other_symbol(symbol))


def get_clients(room_name):
    response = table.get_item(
        Key=generate_key(room_name),
        ConsistentRead=True,
        ExpressionAttributeNames={
            '#x': game.Symbols.X_VALUE,
            '#o': game.Symbols.O_VALUE,
        },
        ProjectionExpression='#x, #o',
    )

    item = response.get('Item')
    if item is not None:
        return {
            game.Symbols.X_VALUE: item.get(game.Symbols.X_VALUE),
            game.Symbols.O_VALUE: item.get(game.Symbols.O_VALUE),
        }
    else:
        return {}


def set_ready(room_name, symbol, ready):
    response = table.update_item(
        Key=generate_key(room_name),
        ExpressionAttributeNames={
            '#symbol': symbol,
            '#client_ready': ClientAttributeNames.READY,
        },
        ExpressionAttributeValues={
            ':ready': ready,
        },
        UpdateExpression='SET #symbol.#client_ready :ready',
        ConditionExpression='attribute_exists(#symbol)',
        ReturnValues='ALL_NEW'
    )

    attributes = response['Attributes']
    return (attributes.get(game.Symbols.X_VALUE, {}).get(ClientAttributeNames.READY, False) and
            attributes.get(game.Symbols.O_VALUE, {}).get(ClientAttributeNames.READY, False))


def set_all_not_ready(room_name):
    clients = get_clients(room_name)

    if game.Symbols.X_VALUE in clients:
        set_ready(room_name, game.Symbols.X_VALUE, False)

    if game.Symbols.O_VALUE in clients:
        set_ready(room_name, game.Symbols.O_VALUE, False)


def clear_symbol(room_name, symbol, connection_id):
    try:
        response = table.update_item(
            Key=generate_key(room_name),
            ExpressionAttributeNames={
                '#symbol': symbol,
                '#client_connection_id': ClientAttributeNames.CONNECTION_ID,
                '#connection_ids': AttributeNames.CONNECTION_IDS,
                '#state': AttributeNames.STATE,
            },
            ExpressionAttributeValues={
                ':connection_id': connection_id,
                ':connection_id_set': {connection_id},
            },
            UpdateExpression='REMOVE #symbol, #state DELETE #connection_ids :connection_id_set',
            ConditionExpression='#symbol.#client_connection_id = :connection_id',
            ReturnValues='ALL_NEW',
        )

        other_symbol = game.get_other_symbol(symbol)
        other_client = response['Attributes'].get(other_symbol)
        if other_client is not None:
            set_ready(room_name, other_symbol, False)
            return other_client[ClientAttributeNames.CONNECTION_ID]
        else:
            remove(room_name)
            return None
    except ClientError as e:
        if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
            raise


def remove(room_name):
    table.delete_item(
        Key=generate_key(room_name),
        ReturnValues='NONE',
    )
