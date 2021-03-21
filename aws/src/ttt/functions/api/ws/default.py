from ttt.logging import logger
from ttt import ws


def lambda_handler(event, context):
    connection_id = ws.get_connection_id(event)
    body = event['body']
    logger.info('Unknown message type from \'%s\': %s', connection_id, body)
    ws.send_message(connection_id, 'unknown_message_type', {
        'error': f'Message of \'{body}\' is invalid or contains an unknown message type'
    })
    return {
        'statusCode': 400,
        'body': 'Unknown message type',
    }
