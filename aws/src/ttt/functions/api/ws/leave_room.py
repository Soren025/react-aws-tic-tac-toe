from ttt.dynamodb import clients_table, rooms_table
from ttt.logging import logger
from ttt import ws


def lambda_handler(event, context):
    connection_id = ws.get_connection_id(event)
    try:
        room_info = clients_table.clear_room(connection_id)
        if room_info is not None:
            room_name = room_info[clients_table.AttributeNames.ROOM_NAME]
            symbol = room_info[clients_table.AttributeNames.SYMBOL]
            other_connection_id = rooms_table.clear_symbol(room_name, symbol, connection_id)
            if other_connection_id is not None:
                ws.send_message(other_connection_id, 'other_left')
            response_payload = {
                'success': True,
                'room_left': room_name,
            }
        else:
            response_payload = {
                'success': False
            }
        ws.send_message(connection_id, 'leave_room_response', response_payload)
        return {
            'statusCode': 200,
            'body': 'Success',
        }
    except Exception as e:
        logger.exception('Error leaving room')
        return {
            'statusCode': 500,
            'body': f'Error: {e}',
        }
