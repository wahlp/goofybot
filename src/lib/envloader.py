import logging
import os

import boto3


ssm = boto3.client('ssm')
parameter_names = [
    ('/goofybot/discord_token', 'DISCORD_TOKEN'),
    ('/goofybot/target_channel', 'TARGET_CHANNEL'),
    ('/goofybot/image_api_lambda_name', 'IMAGE_API_LAMBDA_NAME'),
    ('/goofybot/db/host', 'HOST'),
    ('/goofybot/db/username', 'USERNAME'),
    ('/goofybot/db/password', 'PASSWORD'),
    ('/goofybot/db/database', 'DATABASE'),
    ('/goofybot/db/table/reactions', 'TABLE_REACTIONS'),
    ('/goofybot/db/table/phrases', 'TABLE_PHRASES'),
    ('/goofybot/db/table/phrase_usage', 'TABLE_PHRASE_USAGE'),
    ('/goofybot/db/table/counters', 'TABLE_COUNTERS'),
    ('/goofybot/db/table/counter_incidents', 'TABLE_COUNTER_INCIDENTS')
]

logger = logging.getLogger(__name__)


def load_env_vars():
    for param_name, env_var_name in parameter_names:
        response = ssm.get_parameter(Name=param_name, WithDecryption=True)
        os.environ[env_var_name] = response['Parameter']['Value']

    logging.info(f'loaded {len(parameter_names)} environment variables')


if __name__ == '__main__':
    load_env_vars()