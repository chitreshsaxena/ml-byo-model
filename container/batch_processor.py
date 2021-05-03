import boto3
import urllib3
import os, io, sys, time, argparse, json, random
import numpy as np
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from datetime import datetime
from operator import itemgetter, attrgetter
from time import sleep

# DynamoDB Table Name
DB_TABLE = 'BatchProcessingJob'

# SageMaker Inference endpoint Name
ENDPOINT_NAME = 'Detection-EndPoint'

# Logging Category Types
LOGTYPE_ERROR = 'ERROR'
LOGTYPE_INFO = 'INFO'
LOGTYPE_DEBUG = 'DEBUG'

# S3 Bucket Prefix for uploaded files
INPUT_PREFIX = 'input/'

def pipeline(payload):
    # Invoke SageMaker endpoint
    runtime = boto3.client(service_name='runtime.sagemaker', region_name=os.environ.get('REGION'))
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME, ContentType='text/csv', Body=payload)
    results = response['Body'].read()
    return results

def batch_process(inputBucket, fileName, region):
    s3 = boto3.client('s3')
    startTime = datetime.now()
    filePath = '/tmp/'+fileName

    # Download file from S3
    try:
        s3.download_file(inputBucket, INPUT_PREFIX+fileName, filePath)

    except ClientError as e:
        logMessage(fileName, "Error retrieving file from S3 using `download_fileobj`" + str(e), LOGTYPE_DEBUG)

    # Process file
    try:
        results = ""
        with open(filePath, 'rb') as f:
            payload = f.read()
            results = pipeline(payload)

        with open(filePath, "wb") as ff:
            ff.write(results)

    except Exception as e:
        logMessage(fileName, "Error processing Moviepy Video" + str(e), LOGTYPE_DEBUG)

    # Update processing record in DynamoDB
    try:
        endTime = datetime.now()
        diffTime = endTime - startTime
        logMessage(fileName, "Total processing time - "+str(diffTime.seconds)+'s', LOGTYPE_INFO)
        job_update(
            fileName,
            inputBucket,
            startTime.strftime("%m-%d-%Y-%H:%M:%S.%f")[:-3],
            endTime.strftime("%m-%d-%Y-%H:%M:%S.%f")[:-3],
            str(diffTime.seconds)+'s',
            region
        )

    except Exception as e:
        logMessage(fileName, "Error in DynamoDB `job_update`" + str(e), LOGTYPE_DEBUG)

    # Upload processed file to S3
    try:
        with open(filePath, 'rb') as file:
            s3.upload_fileobj(
                file,
                inputBucket,
                'output/'+endTime.strftime("%m-%d-%Y-%H:%M:%S.%f")[:-3]+'-'+fileName.split('.')[0]+'.csv'
                )

    except ClientError as e:
        logMessage(fileName, "Can't upload to S3 using `upload_fileobj`" + str(e), LOGTYPE_DEBUG)


def job_update(fileName, inputBucket, startTime, endTime, processingTime, region):
    # Update DynamoDB with transaction details
    try:
        dynamodb = boto3.resource('dynamodb', region_name = region)
        table = dynamodb.Table(DB_TABLE)

        table.put_item(
            Item={
                'FileName': fileName,
                'StartTime': startTime,
                'EndTime': endTime,
                'ProcessingTime': processingTime,
                'OutputPath': 's3://'+inputBucket+'/output/'+endTime+'-'+fileName.split('.')[0]+'_out.csv'
            }
        )
        logMessage(fileName, "Added Batch Job details to DynamoDB", LOGTYPE_INFO)

    except Exception as e:
        logMessage(fileName, "Error adding Batch Job Details in DynamoDB" + str(e), LOGTYPE_ERROR)


def logMessage(file, message, logType):

    try:
        logMessageDetails = constructMessageFormat(file, message, '', logType)

        if logType == "INFO" or logType == "ERROR":
            print(logMessageDetails)

        elif logType == "DEBUG":

            try:
                if os.environ.get('DEBUG') == "LOGTYPE":
                   print(logMessageDetails)

            except KeyError:
                pass

    except Exception as e:
        logMessageDetails = constructMessageFormat(file, message, "Error occurred at Batch_processor.logMessage" + str(e), logType)
        print(logMessageDetails)


def constructMessageFormat(file, message, additionalErrorDetails, logType):

    if additionalErrorDetails != '':
        return "File: "+file+" "+logType+": "+ message+" Additional Details -  "+additionalErrorDetails

    else:
        return "File: "+file+" "+logType+": "+message


def main():
    # Capture environment variables
    inputBucket = str(os.environ.get('INPUT_BUCKET'))
    fileName = str(os.environ.get('FILE_NAME').split('/')[-1])
    region = str(os.environ.get('REGION'))

    # Start Image Processing using Environment Variables
    logMessage(fileName, "Starting Processing Batch Job", LOGTYPE_INFO)
    batch_process(inputBucket, fileName, region)


if __name__ == '__main__':
    main()
