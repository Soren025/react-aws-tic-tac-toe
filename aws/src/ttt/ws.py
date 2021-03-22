import json
import os

import boto3

MESSAGE_TYPE_KEY = 'type'
MESSAGE_PAYLOAD_KEY = 'payload'


class MessageTypes:
    JOIN_ROOM_RESPONSE = 'join_room_response'
    LEAVE_ROOM_RESPONSE = 'leave_room_response'
    STATE_CHANGED = 'state_changed'
    OTHER_JOINED = 'other_joined'
    OTHER_LEFT = 'other_left'


ws_client = boto3.client('apigatewaymanagementapi', endpoint_url=os.getenv('WS_CLIENT_ENDPOINT'))


def get_connection_id(event):
    return event['requestContext']['connectionId']


def get_message_payload(event):
    message = json.loads(event['body'])
    return message.get(MESSAGE_PAYLOAD_KEY, None)


def send_message(connection_id, type, payload=None):
    if payload is not None:
        message = {
            MESSAGE_TYPE_KEY: type,
            MESSAGE_PAYLOAD_KEY: payload,
        }
    else:
        message = {
            MESSAGE_TYPE_KEY: type
        }
    print(message)
    ws_client.post_to_connection(
        ConnectionId=connection_id,
        Data=json.dumps(message).encode('utf-8'),
    )
