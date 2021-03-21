from ttt.dynamodb import (
    clients_table,
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
        if symbol is not None:
            clients_table.set_room(connection_id, room_name, symbol)
            other_connection_id = rooms_table.get_other_client(room_name, symbol)
            if other_connection_id is not None:
                ws.send_message(other_connection_id, 'other_joined')
            response_payload = {
                'success': True,
                'symbol': symbol,
            }
        else:
            response_payload = {
                'success': False
            }

        ws.send_message(connection_id, 'join_room_response', response_payload)

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
