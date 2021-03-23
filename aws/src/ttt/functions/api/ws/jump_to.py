from ttt.dynamodb import clients_table, rooms_table
from ttt import utils, ws


def lambda_handler(event, context):
    connection_id = ws.get_connection_id(event)
    room_name = clients_table.get_room(connection_id)

    if room_name is not None:
        payload = ws.get_message_payload(event)
        step = payload['step']

        new_state = jump_to(room_name, step)
        if new_state is not None:
            new_state = utils.replace_decimals(new_state)
            for room_connection_id in rooms_table.get_connection_ids(room_name):
                ws.send_message(room_connection_id, 'state', new_state)


def jump_to(room_name, step):
    room = rooms_table.get(room_name)
    state = room[rooms_table.AttributeNames.STATE]
    version = room[rooms_table.AttributeNames.VERSION]

    history = state[rooms_table.StateAttributeNames.HISTORY]
    if step < 0 or step >= len(history):
        return None

    state[rooms_table.StateAttributeNames.STEP_NUMBER] = step
    state[rooms_table.StateAttributeNames.X_IS_NEXT] = (step % 2) == 0

    return rooms_table.update(room_name, state, version) if state else None
