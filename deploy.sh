#!/bin/bash

# Create a temporary directory for dependencies
mkdir -p package
pip install --target ./package -r requirements.txt

# Create deployment package
cd package
zip -r ../deployment.zip .
cd ..
zip -g deployment.zip lambda_function.py

# Create SNS topic
echo "Creating SNS topic..."
TOPIC_ARN=$(aws sns create-topic --name aws-cost-alert --region us-east-1 --output text)
echo "SNS Topic ARN: $TOPIC_ARN"

# Create IAM role for Lambda
echo "Creating IAM role..."
ROLE_ARN=$(aws iam create-role \
  --role-name aws-cost-alert-lambda-role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Action": "sts:AssumeRole",
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      }
    }]
  }' --output text --query 'Role.Arn')

echo "Attaching policies to role..."
aws iam attach-role-policy \
  --role-name aws-cost-alert-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Create custom policy for Cost Explorer and SNS
aws iam put-role-policy \
  --role-name aws-cost-alert-lambda-role \
  --policy-name cost-explorer-sns-policy \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "ce:GetCostAndUsage",
          "ce:GetCostForecast"
        ],
        "Resource": "*"
      },
      {
        "Effect": "Allow",
        "Action": "sns:Publish",
        "Resource": "'$TOPIC_ARN'"
      }
    ]
  }'

# Wait for role to be ready
echo "Waiting for role to be ready..."
sleep 10

# Create Lambda function
echo "Creating Lambda function..."
aws lambda create-function \
  --function-name aws-cost-alert \
  --runtime python3.9 \
  --handler lambda_function.lambda_handler \
  --role "$ROLE_ARN" \
  --zip-file fileb://deployment.zip \
  --timeout 30 \
  --region us-east-1 \
  --environment Variables={SNS_TOPIC_ARN=$TOPIC_ARN}

# Create CloudWatch Events rule
echo "Creating CloudWatch Events rule..."
aws events put-rule \
  --name DailyCostAlert \
  --schedule-expression "rate(1 day)" \
  --region us-east-1

# Add permission for CloudWatch Events to invoke Lambda
echo "Adding CloudWatch Events permission..."
aws lambda add-permission \
  --function-name aws-cost-alert \
  --statement-id CloudWatchEvents \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn $(aws events describe-rule --name DailyCostAlert --region us-east-1 --query 'Arn' --output text) \
  --region us-east-1

# Add target to CloudWatch Events rule
echo "Adding target to CloudWatch Events rule..."
aws events put-targets \
  --rule DailyCostAlert \
  --targets "Id"="1","Arn"="$(aws lambda get-function --function-name aws-cost-alert --region us-east-1 --query 'Configuration.FunctionArn' --output text)" \
  --region us-east-1

echo "Deployment complete! Please subscribe to the SNS topic with your email:"
echo "aws sns subscribe --topic-arn $TOPIC_ARN --protocol email --notification-endpoint your.email@example.com --region us-east-1"
