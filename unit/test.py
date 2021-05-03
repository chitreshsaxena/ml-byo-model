import boto3
import urllib3
import os, io, sys, time, argparse, json, random
#import cv2
import numpy as np
from botocore.exceptions import ClientError
from datetime import datetime
from operator import itemgetter, attrgetter
from time import sleep
import csv


# SageMaker Inference endpoint Name
ENDPOINT_NAME = 'ObjectDetection-EndPoint'

# Logging Category Types
LOGTYPE_ERROR = 'ERROR'
LOGTYPE_INFO = 'INFO'
LOGTYPE_DEBUG = 'DEBUG'

# S3 Bucket Prefix for uploaded video files
INPUT_PREFIX = 'input/'

def pipeline(payload):
    # Invoke SageMaker endpoint

    #runtime = boto3.client(service_name='runtime.sagemaker', region_name=os.environ.get('REGION'))
    runtime = boto3.client(service_name='runtime.sagemaker', region_name='us-east-2')
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME, ContentType='text/csv', Body=payload)

    results = response['Body'].read()
    #detections = json.loads(results)

    return results

def batch_process(inputBucket, fileName, region):
    s3 = boto3.client('s3')
    startTime = datetime.now()
    filePath = '/tmp/'+fileName
    #outFilePath = '/tmp/'+ fileName.split('.')[0]+'_out.csv'
    #outFilePath = filePath #'/Users/chitress/documents/ChromeDownloads/' + fileName.split('.')[0] + '_out.csv'
    # Download csv file from S3
    try:
        s3.download_file(inputBucket, INPUT_PREFIX+fileName, filePath)
    except ClientError as e:
        logMessage(fileName, "Error retrieving file from S3 using `download_fileobj`" + str(e), LOGTYPE_DEBUG)

    # Process file
    #try:
    results = ""
    with open(filePath, 'rb') as f:
        payload = f.read()
        results = pipeline(payload)

    with open(filePath, "wb") as ff:
        ff.write(results)

    # Upload processed file to S3
    #try:
    endTime = datetime.now()
    #with open('/tmp/'+fileName.split('.')[0]+'.csv', 'rb') as file:
    with open(filePath, "rb") as file:
        #content = file.read()
        #print( content)
        s3.upload_fileobj(
            file,
            inputBucket,
            'output/'+endTime.strftime("%m-%d-%Y-%H:%M:%S.%f")[:-3]+'-'+fileName.split('.')[0]+'.csv'
            )




    #except ClientError as e:
        #print(e)
        #logMessage(fileName, "Can't upload video to S3 using `upload_fileobj`" + str(e), LOGTYPE_DEBUG)


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
    #inputBucket = str(os.environ.get('INPUT_BUCKET'))
    #fileName = str(os.environ.get('FILE_NAME').split('/')[-1])
    #region = str(os.environ.get('REGION'))

    inputBucket = 'achernar'
    fileName = 'sample.csv'
    region = 'us-west-2'

    # Start Processing using Environment Variables
    logMessage(fileName, "Starting Batch Job", LOGTYPE_INFO)
    batch_process(inputBucket, fileName, region)


if __name__ == '__main__':
    main()
