import os

from botocore.exceptions import ClientError

from ttt import game

from . import dynamodb


class AttributeNames:
    ROOM_NAME = 'room_name'
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
            },
            ExpressionAttributeValues={
                ':connection_id': connection_id,
            },
            UpdateExpression='SET #symbol = :connection_id',
            ConditionExpression='attribute_not_exists(#symbol)',
            ReturnValues='NONE',
        )
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return False
        else:
            raise
