# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import sys
import time
import logging

import boto3
from boto3.dynamodb.conditions import Key, Attr
from awsglue.utils import getResolvedOptions

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
glue = boto3.client('glue')
ssm = boto3.client('ssm')


def get_suggestions(table, key_value):
    response = table.query(
        IndexName='table-index',
        KeyConditionExpression=Key('tableHashKey').eq(key_value)
    )
    return response['Items']


def testGlueJob(jobId, count, sec, jobName):
    i = 0
    while i < count:
        logger.info(f'Job name {jobName} with id {jobId}')
        response = glue.get_job_run(JobName=jobName, RunId=jobId)
        status = response['JobRun']['JobRunState']
        logger.info(f'Job name {jobName} with id {jobId} is in status: {status}')
        if status == 'SUCCEEDED':
            return 1
        elif (status == 'RUNNING' or status == 'STARTING' or status == 'STOPPING'):
            time.sleep(sec)
            i += 1
        else:
            return 0
        if i == count:
            return 0


# Required Parameters
args = getResolvedOptions(sys.argv, [
    'env',
    'glueSuggestionVerificationJob',
    'glueVerificationJob',
    'glueProfilerJob',
    'glueDatabase',
    'glueTables'])

env = args['env']
logger.info(f'Environment is {env}')
table_suffix = env
suggestion_dynamodb_table_name = f"DataQualitySuggestion-{table_suffix}"
analysis_dynamodb_table_name = f"DataQualityAnalyzer-{table_suffix}"
suggestions_job_name = args['glueSuggestionVerificationJob']
verification_job_name = args['glueVerificationJob']
profile_job_name = args['glueProfilerJob']
glue_database = args['glueDatabase']
glue_tables = [x.strip() for x in args['glueTables'].split(',')]

# Determine which tables had Deequ data quality suggestions set up already
suggestions_tables = []
verification_tables = []
suggestions_dynamo = dynamodb.Table(suggestion_dynamodb_table_name)
for table in glue_tables:
    suggestions_item = get_suggestions(
        suggestions_dynamo, f"{glue_database}-{table}")
    if suggestions_item:
        verification_tables.append(table)
    else:
        suggestions_tables.append(table)

logger.info('Calling Glue Jobs')
if suggestions_tables:
    suggestions_response = glue.start_job_run(
        JobName=suggestions_job_name,
        Arguments={
            '--dynamodbSuggestionTableName': suggestion_dynamodb_table_name,
            '--dynamodbAnalysisTableName': analysis_dynamodb_table_name,
            '--glueDatabase': glue_database,
            '--glueTables': ','.join(suggestions_tables)
        }
    )
    logger.info(f'Suggestions_response is : {suggestions_response}')
if verification_tables:
    verification_response = glue.start_job_run(
        JobName=verification_job_name,
        Arguments={
            '--dynamodbSuggestionTableName': suggestion_dynamodb_table_name,
            '--dynamodbAnalysisTableName': analysis_dynamodb_table_name,
            '--glueDatabase': glue_database,
            '--glueTables': ','.join(verification_tables)
        }
    )
    logger.info(f'Verification_response is : {verification_response}')

profile_response = glue.start_job_run(
    JobName=profile_job_name,
    Arguments={
        '--glueDatabase': glue_database,
        '--glueTables': ','.join(glue_tables)
    }
)
logger.info(f'Profile_response is : {profile_response}')

# Wait for execution to complete, timeout in 60*30=1800 secs
logger.info('Waiting for execution')
message = 'Error during Controller execution - Check logs'
if suggestions_tables:
    if testGlueJob(suggestions_response['JobRunId'], 60, 30, suggestions_job_name) != 1:
        raise ValueError(message)
if verification_tables:
    if testGlueJob(verification_response['JobRunId'], 60, 30, verification_job_name) != 1:
        raise ValueError(message)
if testGlueJob(profile_response['JobRunId'], 60, 30, profile_job_name) != 1:
    raise ValueError(message)
