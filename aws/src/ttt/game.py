class Symbols:
    X_VALUE = 'X'
    O_VALUE = 'O'


def get_other_symbol(symbol):
    if symbol == Symbols.X_VALUE:
        return Symbols.O_VALUE
    elif symbol == Symbols.O_VALUE:
        return Symbols.X_VALUE
    else:
        return None
