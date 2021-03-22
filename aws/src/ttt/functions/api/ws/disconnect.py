from ttt.dynamodb import clients_table, rooms_table
from ttt.logging import logger
from ttt import ws


def lambda_handler(event, context):
    connection_id = ws.get_connection_id(event)
    logger.info('Client disconnect: %s', connection_id)
    room_info = clients_table.remove(connection_id)
    if room_info is not None:
        room_name = room_info[clients_table.AttributeNames.ROOM_NAME]
        symbol = room_info[clients_table.AttributeNames.SYMBOL]
        logger.info('Removing disconnected client from room: room_name=%s symbol=%s', room_name, symbol)
        other_connection_id = rooms_table.clear_symbol(room_name, symbol, connection_id)
        if other_connection_id is not None:
            ws.send_message(other_connection_id, ws.MessageTypes.OTHER_LEFT)
    return {
        'statusCode': 200,
        'body': 'Success',
    }
