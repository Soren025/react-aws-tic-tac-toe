from ttt.dynamodb import (
    clients_table,
    rooms_table,
)
from ttt import game
from ttt.logging import logger
from ttt import ws


def lambda_handler(event, context):
    connection_id = ws.get_connection_id(event)
    try:
        payload = ws.get_message_payload(event)
        room_name = payload['room_name']

        symbol = rooms_table.join_room(room_name, connection_id)
        if symbol is not None:
            clients_table.set_room(connection_id, room_name, symbol)

            clients = rooms_table.get_clients(room_name)
            x_client = clients.get(game.Symbols.X_VALUE, {})
            o_client = clients.get(game.Symbols.O_VALUE, {})
            other_client = clients.get(game.get_other_symbol(symbol))

            if other_client is not None:
                ws.send_message(other_client[rooms_table.ClientAttributeNames.CONNECTION_ID], ws.MessageTypes.OTHER_JOINED)

            response_payload = {
                'success': True,
                'symbol': symbol,
                'state': rooms_table.get_state(room_name),
                'x_ready': x_client.get(rooms_table.ClientAttributeNames.READY, False),
                'o_ready': o_client.get(rooms_table.ClientAttributeNames.READY, False),
            }
        else:
            response_payload = {
                'success': False
            }

        ws.send_message(connection_id, ws.MessageTypes.JOIN_ROOM_RESPONSE, response_payload)

        return {
            'statusCode': 200,
            'body': 'Success',
        }
    except Exception as e:
        logger.exception('Error joining room')
        ws.send_message(connection_id, 'error')
        return {
            'statusCode': 500,
            'body': f'Error: {e}',
        }
