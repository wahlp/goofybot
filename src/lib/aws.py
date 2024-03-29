import asyncio
import concurrent
import io
import json
import logging
import os

import boto3
import botocore

logger = logging.getLogger(__name__)

class LambdaClient():
    def __init__(self, session: boto3.Session, concurrency: int = 20):
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=concurrency,
        )
        client_config = botocore.config.Config(
           max_pool_connections=concurrency,
           retries={'max_attempts': 0},
           read_timeout=120
        )
        self.client = session.client('lambda', config=client_config)
    
    async def invoke_async(self, event_parameters):
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(self.executor, lambda: self.invoke(event_parameters))
        return result

    def invoke(self, event_parameters):
        logger.info('invoking lambda')
        response = self.client.invoke(
            FunctionName=os.getenv('IMAGE_API_LAMBDA_NAME'),
            InvocationType='RequestResponse',
            Payload=json.dumps(event_parameters)
        )
        logger.info('lambda response received')
        if 'StatusCode' not in response or response['StatusCode'] != 200:
            raise ValueError(f'Lambda invocation failed with response {response}')
        output = response["Payload"].read()
        return output
    

class APITimeoutError(Exception):
    pass

async def invoke_image_processing_lambda(
    image_type: str,
    image_url: str, 
    text: str, 
    font: str, 
    transparency: bool, 
    speedup: float = None,
    compress_color: bool = None,
    compress_file: bool = None
):
    if os.getenv('IMAGE_API_LAMBDA_NAME') is None:
        raise Exception('image API was called but lambda name was not set')
    
    session = boto3.Session()
    lambda_client = LambdaClient(session)

    event_parameters = {
        "image_type": image_type,
        "url": image_url,
        "text": text,
        "font": font,
        "transparency": transparency
    }

    if speedup is not None:
        event_parameters["speed"] = speedup
    if compress_color is not None:
        event_parameters["compress_color"] = compress_color
    if compress_file is not None:
        event_parameters["compress_file"] = compress_file

    response_payload = await lambda_client.invoke_async(event_parameters)
    lambda_response = json.loads(response_payload)
    logger.info(lambda_response)

    if 'body' not in lambda_response:
        raise APITimeoutError(f'The lambda timed out before it could process the {image_type}')

    bucket_name = lambda_response['body']['bucket_name']
    object_key = lambda_response['body']['file_name']

    logger.info('calling s3')
    s3_client = session.client('s3')
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    object_data = response['Body'].read()
    logger.info(f'received s3 object of size {len(object_data)}')

    buffer = io.BytesIO(object_data)
    return buffer
