import asyncio
import concurrent
import json
import os

import boto3
import botocore


class LambdaClient():
    def __init__(self, concurrency: int = 20):
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=concurrency,
        )
        client_config = botocore.config.Config(
           max_pool_connections=concurrency
        )
        self.client = boto3.client('lambda', config=client_config)
    
    async def invoke_async(self, event_parameters):
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(self.executor, lambda: self.invoke(event_parameters))
        return result

    def invoke(self, event_parameters):
        response = self.client.invoke(
            FunctionName=os.getenv('IMAGE_API_LAMBDA_NAME'),
            InvocationType='RequestResponse',
            Payload=json.dumps(event_parameters)
        )
        if 'StatusCode' not in response or response['StatusCode'] != 200:
            raise ValueError(f'Lambda invocation failed with response {response}')
        output = response["Payload"].read()
        return output