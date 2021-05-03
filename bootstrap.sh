#!/bin/bash

echo -n "Enter the AWS Region to use > "
read REGION
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text --region $REGION)
STACKNAME="MlOps"
BOOTSTRAP_BUCKET="$(echo $STACKNAME | awk '{ print tolower($0) }')-${REGION}-bootstrap-${AWS_ACCOUNT_ID}"

echo ""
echo -n "Creating Bootstrap S3 Bucket ..."
echo ""
aws s3 mb "s3://${BOOTSTRAP_BUCKET}" --region $REGION
aws s3api put-bucket-versioning --bucket $BOOTSTRAP_BUCKET --versioning-configuration Status=Enabled --region $REGION



echo ""
echo -n "Packaging Build Artifacts ..."
echo ""
cd ./container
zip -r ../staging/container-src.zip Dockerfile batch_processor.py environment.yml
aws s3 cp ../staging/container-src.zip "s3://${BOOTSTRAP_BUCKET}/artifacts/" --region $REGION
cd ../

echo ""
echo -n "Packaging Model Artifacts ..."
echo ""
aws s3 cp ./model/model.tar.gz "s3://${BOOTSTRAP_BUCKET}/artifacts/" --region $REGION


echo ""
echo -n "Deploying CloudFormation Stack ..."
echo ""
aws cloudformation deploy --stack-name $STACKNAME --template-file ./solution-cfn-template.yaml --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND --parameter-overrides S3BootstrapBucket=$BOOTSTRAP_BUCKET --region $REGION
