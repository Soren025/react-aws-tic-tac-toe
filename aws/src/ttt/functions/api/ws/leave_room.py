from ttt.dynamodb import clients_table, rooms_table
from ttt.logging import logger
from ttt import ws


def lambda_handler(event, context):
    connection_id = ws.get_connection_id(event)
    room_name = clients_table.clear_room(connection_id)
    if room_name is not None:
        logger.info('Client left room: connection_id=%s room_name=%s', connection_id, room_name)
        rooms_table.leave_room(room_name, connection_id)
    return {
        'statusCode': 200,
        'body': 'Success',
    }
