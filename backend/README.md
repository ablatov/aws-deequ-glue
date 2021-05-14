<!--
title: 'AWS Serverless REST API with DynamoDB in Python'
description: 'Backend part for Data Quality solution.'
platform: AWS
language: Python
-->

## Setup
```bash
cd backend
make install
source ./py37/bin/activate
```

## Deploy
In order to deploy simply run
```bash
serverless deploy
```

The expected result should be similar to:

```bash
Serverless: Packaging service…
Serverless: Uploading CloudFormation file to S3…
Serverless: Uploading service .zip file to S3…
Serverless: Updating Stack…
Serverless: Checking Stack update progress…
Serverless: Stack update finished…

service: dq-backend-dynamodb
stage: dev
region: us-east-1
stack: dq-backend-dynamodb-dev
resources: 6
resources: 25
api keys:
  None
endpoints:
  GET - https://svu0xiy50e.execute-api.us-east-1.amazonaws.com/dev/suggestions
  POST - https://svu0xiy50e.execute-api.us-east-1.amazonaws.com/dev/suggestions
  PUT - https://svu0xiy50e.execute-api.us-east-1.amazonaws.com/dev/suggestions
  DELETE - https://svu0xiy50e.execute-api.us-east-1.amazonaws.com/dev/suggestions/{suggestion_id}
  GET - https://svu0xiy50e.execute-api.us-east-1.amazonaws.com/dev/analyzers
  POST - https://svu0xiy50e.execute-api.us-east-1.amazonaws.com/dev/analyzers
  PUT - https://svu0xiy50e.execute-api.us-east-1.amazonaws.com/dev/analyzers
  DELETE - https://svu0xiy50e.execute-api.us-east-1.amazonaws.com/dev/analyzers/{analyzer_id}
functions:
  constraintsApi: dq-backend-dynamodb-dev-constraintsApi
layers:
  None
```
