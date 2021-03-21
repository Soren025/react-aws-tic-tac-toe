from ttt.logging import logger
from ttt import ws


def lambda_handler(event, context):
    logger.info('Unknown message type from \'%s\': %s', ws.get_connection_id(event), event['body'])
    return {
        'statusCode': 400,
        'body': 'Unknown message type',
    }
