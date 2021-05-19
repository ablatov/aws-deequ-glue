import logging
import os
import time
import uuid

from flask import Flask, jsonify, request

import boto3
app = Flask(__name__)

dynamodb = boto3.resource('dynamodb')

SUGGESTIONS_TABLE = os.environ['SUGGESTION_DYNAMODB_TABLE']
ANALYZERS_TABLE = os.environ['ANALYZER_DYNAMODB_TABLE']

CONSTRAINT_ID = '<constraint_id>'

ROOT_SUGGESTIONS = '/suggestions'
DELETE_SUGGESTION = f'{ROOT_SUGGESTIONS}/{CONSTRAINT_ID}'

ROOT_ANALYZERS = '/analyzers'
DELETE_ANALYZER = f'{ROOT_ANALYZERS}/{CONSTRAINT_ID}'


def handle_table_name(endpoint):
    return SUGGESTIONS_TABLE if 'suggestions' in endpoint else ANALYZERS_TABLE


@app.after_request
def apply_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With'
    return response


@app.route(ROOT_SUGGESTIONS, methods=["GET"])
@app.route(ROOT_ANALYZERS, methods=["GET"])
def list_constraints():
    table_name = handle_table_name(request.path)

    table = dynamodb.Table(table_name)
    result = table.scan()

    response = {
        "statusCode": 200,
        "body": result['Items']
    }

    return jsonify(response)


@app.route(ROOT_SUGGESTIONS, methods=["PUT"])
@app.route(ROOT_ANALYZERS, methods=["PUT"])
def enable_constraint():
    data = request.json
    if 'id' not in data:
        logging.error("Validation Failed")
        raise Exception("Couldn't update item.")

    timestamp = str(time.time())

    table_name = handle_table_name(request.path)
    table = dynamodb.Table(table_name)
    result = table.update_item(
        Key={
            'id': data['id']
        },
        UpdateExpression='SET #enable = :e, '
                         'updatedAt = :updatedAt',
        ExpressionAttributeNames={
            '#enable': 'enable',
        },
        ExpressionAttributeValues={
            ':e': data['enable'],
            ':updatedAt': timestamp,
        },

        ReturnValues='ALL_NEW',
    )

    response = {
        "statusCode": 200,
        "body": result['Attributes']
    }
    return jsonify(response)


@app.route(DELETE_SUGGESTION, methods=["DELETE"])
@app.route(DELETE_ANALYZER, methods=["DELETE"])
def delete_constraint(constraint_id):
    table_name = handle_table_name(request.path)
    table = dynamodb.Table(table_name)
    table.delete_item(
        Key={
            'id': constraint_id
        }
    )
    response = {
        "statusCode": 200
    }

    return jsonify(response)


@app.route(ROOT_SUGGESTIONS, methods=["POST"])
@app.route(ROOT_ANALYZERS, methods=["POST"])
def create_constraint():
    data = request.json
    if 'tableHashKey' not in data:
        logging.error("Validation Failed")
        raise Exception("Couldn't create suggestion.")

    timestamp = str(time.time())
    table_name = handle_table_name(request.path)
    table = dynamodb.Table(table_name)

    item = {
        'id': str(uuid.uuid1()),
        'column': data['column'],
        'createdAt': timestamp,
        'enable': data['enable'],
        'tableHashKey': data['tableHashKey'],
        'updatedAt': timestamp,
    }

    if table_name == SUGGESTIONS_TABLE:
        typename = 'DataQualitySuggestion'
        item['__typename'] = typename
        item['constraint'] = data['constraint']
        item['constraintCode'] = data['constraintCode']
    else:
        typename = 'DataQualityAnalyzer'
        item['__typename'] = typename
        item['analyzerCode'] = data['analyzerCode']

    table.put_item(Item=item)
    response = {
        "statusCode": 200,
        "body": item
    }

    return jsonify(response)


if __name__ == '__main__':
    app.run()
