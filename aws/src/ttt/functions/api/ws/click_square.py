from ttt.dynamodb import clients_table, rooms_table
from ttt import utils, ws


WINNING_LINES = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6],
]


def lambda_handler(event, context):
    connection_id = ws.get_connection_id(event)
    room_name = clients_table.get_room(connection_id)

    if room_name is not None:
        payload = ws.get_message_payload(event)
        index = payload['index']

        new_state = handle_click(room_name, index)
        if new_state is not None:
            new_state = utils.replace_decimals(new_state)
            for room_connection_id in rooms_table.get_connection_ids(room_name):
                ws.send_message(room_connection_id, 'state', new_state)


def handle_click(room_name, index):
    room = rooms_table.get(room_name)
    state = room[rooms_table.AttributeNames.STATE]
    version = room[rooms_table.AttributeNames.VERSION]

    x_is_next = state[rooms_table.StateAttributeNames.X_IS_NEXT]
    step_number = state[rooms_table.StateAttributeNames.STEP_NUMBER]
    history = state[rooms_table.StateAttributeNames.HISTORY][0:step_number + 1]

    squares = history[-1]
    if squares[index] is not None or calculate_winner(squares):
        return None

    new_squares = squares.copy()
    new_squares[index] = state[rooms_table.StateAttributeNames.X_IS_NEXT] if 'X' else 'O'

    new_state = {
        rooms_table.StateAttributeNames.HISTORY: history.append(new_squares),
        rooms_table.StateAttributeNames.STEP_NUMBER: step_number + 1,
        rooms_table.StateAttributeNames.X_IS_NEXT: not x_is_next
    }

    return rooms_table.update(room_name, new_state, version) if new_state else None


def calculate_winner(squares):
    for line in WINNING_LINES:
        symbol = squares[line[0]]
        if symbol is not None and symbol == squares[line[1]] and symbol == squares[line[2]]:
            return symbol
    return None
