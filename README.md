# AWS Cost Alert System

This system provides daily AWS cost alerts via email using AWS Lambda and SNS.


## Features
- Daily AWS cost monitoring
- Cost forecast for the next 30 days
- Email notifications via SNS
- Serverless deployment using AWS Lambda

## Prerequisites
1. AWS Account with appropriate permissions
2. AWS CLI configured locally
3. Python 3.8 or higher

## Required AWS Services
- AWS Lambda
- AWS SNS
- AWS Cost Explorer
- AWS CloudWatch Events (for scheduling)

## Setup Instructions

1. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Run tests:
```bash
python -m pytest test_lambda_function.py -v
```

3. Create an SNS Topic:
```bash
aws sns create-topic --name aws-cost-alert
```

4. Subscribe your email to the SNS topic:
```bash
aws sns subscribe --topic-arn <YOUR_TOPIC_ARN> --protocol email --notification-endpoint your.email@example.com
```

5. Create a Lambda function:
   - Create a new Lambda function using Python 3.8+ runtime
   - Upload the contents of this directory as a ZIP file
   - Set the environment variable `SNS_TOPIC_ARN` to your SNS topic ARN

6. Set up IAM permissions for the Lambda function:
   - AWSLambdaBasicExecutionRole
   - Allow ce:GetCostAndUsage
   - Allow ce:GetCostForecast
   - Allow sns:Publish

7. Create a CloudWatch Events rule to trigger the Lambda function daily:
```bash
aws events put-rule --name DailyCostAlert --schedule-expression "rate(1 day)"
```

8. Add permission for CloudWatch Events to trigger the Lambda function:
```bash
aws lambda add-permission --function-name aws-cost-alert \
  --statement-id CloudWatchEvents \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn <YOUR_CLOUDWATCH_RULE_ARN>
```

## Cost Considerations
- AWS Lambda: Free tier includes 1M requests per month
- AWS SNS: Free tier includes 1M publishes per month
- AWS Cost Explorer: $0.01 per API request (no free tier)
- Total estimated cost: Less than $1/month for daily alerts

## Customization
You can modify the `lambda_function.py` to:
- Change the monitoring period
- Add more metrics
- Customize the email format
- Add cost thresholds and alerts
