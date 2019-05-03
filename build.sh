#!/bin/bash
region=$1
lambdabucket=$2
stackname=$3
bucket=$4
key=$5
topic=$6

aws --region $region cloudformation package --template-file template.yaml --s3-bucket $lambdabucket --output-template-file package.yaml
aws --region $region cloudformation deploy --template-file package.yaml --stack-name $stackname --capabilities CAPABILITY_IAM --parameter-overrides Bucket=$bucket Key=$key Topic=$topic
