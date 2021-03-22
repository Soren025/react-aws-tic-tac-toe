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
        room_info = clients_table.get_room(connection_id)
        room_name = room_info[clients_table.AttributeNames.ROOM_NAME]
        symbol = room_info[clients_table.AttributeNames.SYMBOL]

        clients = rooms_table.get_clients(room_name)
        x_client = clients.get(game.Symbols.X_VALUE, {})
        o_client = clients.get(game.Symbols.O_VALUE, {})

        if rooms_table.set_ready(room_name, symbol, True):
            state_update = {
                'state': rooms_table.start_game(room_name),
                'x_ready': True,
                'o_ready': True,
            }
        else:
            state_update = {
                'state': rooms_table.get_state(room_name),
                'x_ready': x_client.get(rooms_table.ClientAttributeNames.READY, False),
                'o_ready': o_client.get(rooms_table.ClientAttributeNames.READY, False),
            }

        x_connection_id = x_client.get(rooms_table.ClientAttributeNames.CONNECTION_ID)
        if x_connection_id is not None:
            ws.send_message(x_connection_id, ws.MessageTypes.STATE_CHANGED, state_update)

        o_connection_id = o_client.get(rooms_table.ClientAttributeNames.CONNECTION_ID)
        if o_connection_id is not None:
            ws.send_message(o_connection_id, ws.MessageTypes.STATE_CHANGED, state_update)

    except Exception as e:
        logger.exception('Error setting ready')
        ws.send_message(connection_id, 'error')
        return {
            'statusCode': 500,
            'body': f'Error: {e}',
        }
