from ttt.dynamodb import clients_table
from ttt.logging import logger
from ttt import ws


def lambda_handler(event, context):
    connection_id = ws.get_connection_id(event)
    clients_table.remove(connection_id)
    logger.info('Disconnected: %s', connection_id)
    return {
        'statusCode': 200,
        'body': 'Success',
    }
