## BYO Model Artifacts

This solution allows you to bring your own Model and custom docker image using AWS Batch and SageMaker. In this example we are using a trained model with supervised learning to build a credit card fraud detection system. This will get Inferences for an entire dataset with Batch Transform.

## Repo structure

```bash
├── bootstrap.sh                <-- Bash script for creating bootstrap S3 bucket, uploading artifacts & deploying CloudFormation Stack
├── solution-cfn-template.yaml  <-- CloudFormation to deploy the infrastructure
├── README.md                   <-- This instructions file
├── container                   <-- Directory for container artifacts
│   ├── batch_processor.py      <-- Python code to Invoke SageMaker endpoint
│   ├── Dockerfile              <-- Docker image for creating the container to manage the inference using SageMaker
│   └── environment.yml         <-- File to create the environment for Conda
└── model		                    <-- Directory for model artifact
    ├── model.tar.gz            <-- Trained model for Fraud detection using XGBoost and Random Cut Forest with binary classification.
├── sample                      <-- Directory for dataset
│   ├── creditcard.zip          <-- The labeled dataset used to train & test the model. It contains only numerical features.
│   ├── sample.csv		          <-- Sample dataset to validate the model after deployment
└── staging		                  <-- Temp Directory used by bash script for packaging build artifacts
└── unit		                    <-- Directory containing code to perform batch processor unit test
```

## What's Included

This project contains:
* Custom model: trained model with supervised learning
* Container: Container definition that will host the model.
* CloudFormation:  CloudFormation template needed to deploy the infrastructure.
* Dataset: This contains labeled dataset. It contains only numerical features, because the original features have been transformed for confidentiality using PCA. The dataset used to demonstrated the fraud detection solution has been collected and analyzed during a research collaboration of Worldline and the Machine Learning Group (http://mlg.ulb.ac.be) of ULB (Université Libre de Bruxelles) on big data mining and fraud detection. https://github.com/awslabs/fraud-detection-using-machine-learning/blob/master/source/notebooks/sagemaker_fraud_detection.ipynb


## Requirements

 [Install AWS CLI locally]( https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html)


## Getting Started

All command line directions in this documentation assume you are in the ‘ml-byo’ directory. Navigate there now, if you aren't there already.

1. Navigate to the ‘ml-byo’ directory
2. bash (run the bootstrap.sh):
  >sh bootstrap.sh
  <This will prompt for the region in the command line>
  Enter AWS region to use (e.g. us-west-2)

This will take about 10 mins as it spins up all the resources with the A. B. C. steps as below.

A.	Create Bootstrap S3 Bucket
B.	Package Build & Model Artifacts and upload to S3 bucket
C.  Deploy CloudFormation Stack with the below resources.

---
| Logical ID | Type|
|-|-|
| AutoScaling | AWS::ApplicationAutoScaling::ScalableTarget|
| AutoScalingPolicy | AWS::ApplicationAutoScaling::ScalingPolicy|
| BatchProcessBucketPermission | AWS::Lambda::Permission|
| BatchProcessRepository	|		AWS::ECR::Repository|
| BatchProcessS3Bucket	|		AWS::S3::Bucket|
| BatchProcessingDynamoDBTable	|	AWS::DynamoDB::Table|
| BatchProcessingJobDefinition	|	AWS::Batch::JobDefinition|
| BatchProcessingJobQueue	|	AWS::Batch::JobQueue|
| BatchProcessingLambdaInvokeFunction	| AWS::Lambda::Function|
| BatchServiceRole | AWS::IAM::Role|
| CodeBuildRole | AWS::IAM::Role|
| ComputeEnvironment	|	AWS::Batch::ComputeEnvironment|
| ContainerBuildLambda	|		AWS::Lambda::Function|
| ContainerBuildProject	 |		AWS::CodeBuild::Project|
| EcsInstanceRole | AWS::IAM::Role|
| Sagemaker Endpoint	|		AWS::SageMaker::Endpoint|
| Sagemaker EndpointConfig	|	AWS::SageMaker::EndpointConfig|
| IamInstanceProfile	|		AWS::IAM::InstanceProfile|
| InternetGateway | AWS::EC2::InternetGateway|
| LambdaExecutionRole	 |		AWS::IAM::Role|
| Model | 	AWS::SageMaker::Model|
| Route | 	AWS::EC2::Route|
| RouteTable | AWS::EC2::RouteTable|
| SageMakerRole | AWS::IAM::Role|
| SecurityGroup | AWS::EC2::SecurityGroup|
| StartContainerBuild | Custom::StartContainerBuild|
| Subnet | 	AWS::EC2::Subnet|
| SubnetRouteTableAssociation	 |	AWS::EC2::SubnetRouteTableAssociation|
| VPC | 	AWS::EC2::VPC|
| VPCGatewayAttachment | AWS::EC2::VPCGatewayAttachment |
---

## Validate the Inference of the deployed fraud detection model to make a prediction

1.	Go to S3 bucket batch-processing-job-<Region>-<Account ID>
2.	Create a folder with name as “input”
3.	Upload the sample CSV from ml-byo/sample/sample.csv to input folder of the S3 bucket. This will trigger the batch job which will invoke the SageMaker endpoint. The output file will be saved in the S3 bucket.
4.	After few minutes you should see the output folder in the S3 bucket. Navigate to the output folder and download the <timestamp>-sample.csv file.
5.	The output should look like as indicated below, with each record corresponds to each row of the input file.
0.000260044, 0.000412545, 0.001004696, 0.0000873892495292, 0.977230012, 0.970581293, 0.445608526
Each record is classified as normal (class “0”) or fraudulent (class “1” )

## Clean up
1.	Delete the S3 bucket mlops-<Region>-bootstrap-<Account ID>
2.  Delete the S3 bucket batch-processing-job-<Region>-<Account ID>
2.	Delete the CloudFormation stack MLOps. This will start deleting the resources and will take about 3 mins.
