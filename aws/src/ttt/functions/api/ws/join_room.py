from ttt.dynamodb import (
    # clients_table,
    rooms_table,
)
from ttt.logging import logger
from ttt import ws


def lambda_handler(event, context):
    try:
        connection_id = ws.get_connection_id(event)
        payload = ws.get_message_payload(event)
        room_name = payload['room_name']

        symbol = rooms_table.join_room(room_name, connection_id)
        logger.info(symbol)
        ws.send_message(connection_id, 'join_room_response', {
            'symbol': symbol
        })
        logger.info('send_message?')

        return {
            'statusCode': 200,
            'body': 'Success',
        }
    except Exception as e:
        logger.exception('Error joining room')
        return {
            'statusCode': 500,
            'body': f'Error: {e}',
        }
