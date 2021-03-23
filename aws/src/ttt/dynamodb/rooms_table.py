import os

from botocore.exceptions import ClientError

from . import dynamodb


class AttributeNames:
    ROOM_NAME = 'room_name'
    CONNECTION_IDS = 'connection_ids'
    STATE = 'state'
    VERSION = 'version'


class StateAttributeNames:
    HISTORY = 'history'
    STEP_NUMBER = 'step_number'
    X_IS_NEXT = 'x_is_next'


NEW_ROOM_STATE = {
    StateAttributeNames.HISTORY: [[None] * 9],
    StateAttributeNames.STEP_NUMBER: 0,
    StateAttributeNames.X_IS_NEXT: True,
}

NEW_ROOM_VERSION = 0

table = dynamodb.Table(os.getenv('ROOMS_TABLE_NAME'))


def generate_key(room_name):
    return {
        AttributeNames.ROOM_NAME: room_name
    }


def join_room(room_name, connection_id):
    response = table.update_item(
        Key=generate_key(room_name),
        ExpressionAttributeNames={
            '#connection_ids': AttributeNames.CONNECTION_IDS,
            '#state': AttributeNames.STATE,
            '#version': AttributeNames.VERSION,
        },
        ExpressionAttributeValues={
            ':connection_id': {connection_id},
            ':new_room_state': NEW_ROOM_STATE,
            ':new_room_version': NEW_ROOM_VERSION,
        },
        UpdateExpression='ADD #connection_ids :connection_id SET #state = if_not_exists(#state, :new_room_state), #version = if_not_exists(#version, :new_room_version)',
        ReturnValues='ALL_NEW',
    )

    return response['Attributes'][AttributeNames.STATE]


def leave_room(room_name, connection_id):
    key = generate_key(room_name)

    response = table.update_item(
        Key=key,
        ExpressionAttributeNames={
            '#connection_ids': AttributeNames.CONNECTION_IDS,
        },
        ExpressionAttributeValues={
            ':connection_id': {connection_id},
        },
        UpdateExpression='DELETE #connection_ids :connection_id',
        ReturnValues='UPDATED_NEW'
    )

    if len(response.get('Attributes', {}).get(AttributeNames.CONNECTION_IDS, [])) == 0:
        table.delete_item(
            Key=key,
            ReturnValues='NONE',
        )


def get(room_name):
    response = table.get_item(
        Key=generate_key(room_name),
        ConsistentRead=True,
        ExpressionAttributeNames={
            '#state': AttributeNames.STATE,
            '#version': AttributeNames.VERSION,
        },
        ProjectionExpression='#state, #version',
    )

    return response.get('Item')


def update(room_name, state, expected_version):
    try:
        table.update_item(
            Key=generate_key(room_name),
            ExpressionAttributeNames={
                '#state': AttributeNames.STATE,
                '#version': AttributeNames.VERSION,
            },
            ExpressionAttributeValues={
                ':state': state,
                ':version_increment': 1,
                ':expected_version': expected_version,
            },
            UpdateExpression='SET #state = :state, #version = #version + :version_increment',
            ConditionExpression='#version = :expected_version',
            ReturnValues='NONE'
        )
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return False
        else:
            raise


def get_connection_ids(room_name):
    response = table.get_item(
        Key=generate_key(room_name),
        ConsistentRead=True,
        ExpressionAttributeNames={
            '#connection_ids': AttributeNames.CONNECTION_IDS,
        },
        ProjectionExpression='#connection_ids',
    )

    return response.get('Item', {}).get(AttributeNames.CONNECTION_IDS, [])
