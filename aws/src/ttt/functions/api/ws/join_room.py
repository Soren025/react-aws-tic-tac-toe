from ttt.dynamodb import (
    clients_table,
    rooms_table,
)
from ttt.logging import logger
from ttt import utils, ws


def lambda_handler(event, context):
    connection_id = ws.get_connection_id(event)
    payload = ws.get_message_payload(event)
    room_name = payload['room_name']

    old_room_name = clients_table.set_room(connection_id, room_name)
    if old_room_name is not None:
        logger.info('Client left room: connection_id=%s room_name=%s', connection_id, old_room_name)
        rooms_table.leave_room(old_room_name, connection_id)

    room_state = rooms_table.join_room(room_name, connection_id)
    room_state = utils.replace_decimals(room_state)
    logger.info('Client joined room: connection_id=%s room_name=%s', connection_id, room_name)

    ws.send_message(connection_id, 'state', room_state)

    return {
        'statusCode': 200,
        'body': 'Success',
    }
