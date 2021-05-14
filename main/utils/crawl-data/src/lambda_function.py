# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import os
import logging

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client('glue')


def lambda_handler(event, context):
    """Crawl Data using specified Glue Crawler

    Arguments:
        event {dict} -- Dictionary with details on Bucket and Keys
        context {dict} -- Dictionary with details on Lambda context

    Returns:
        {dict} -- Dictionary with Data Quality Job details
    """
    try:
        crawler_name = os.environ['GLUE_CRAWLER']
        logger.info(f"Starting Crawler {crawler_name}")
        try:
            client.start_crawler(Name=crawler_name)
        except client.exceptions.CrawlerRunningException:
            logger.info('Crawler is already running')
    except Exception as e:
        logger.error('Fatal error', exc_info=True)
        raise e
    return 200
