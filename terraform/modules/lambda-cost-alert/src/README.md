# Lambda Function: AWS Cost Alert

Technical documentation for the AWS Cost Alert Lambda function.

## Function Overview

The Lambda function performs these operations:
1. Retrieves current month's cost data from AWS Cost Explorer
2. Calculates daily and monthly metrics
3. Generates cost forecasts
4. Sends formatted notifications via SNS

## Code Structure

```python
# lambda_function.py
def get_cost_data():
    # Retrieves and processes cost data
    # Returns dict with cost metrics

def send_sns_notification(cost_data):
    # Formats and sends SNS notification
    # Returns None

def lambda_handler(event, context):
    # Main entry point
    # Orchestrates the cost alert process
```

## Cost Calculations

1. **Daily Costs**
   - Yesterday's actual cost
   - Daily average (month-to-date cost / days so far)
   - Daily run rate
   - Day-over-day trend

2. **Monthly Projections**
   - Month-to-date total
   - Projected end-of-month cost
   - Trend analysis
   - Percentage changes

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SNS_TOPIC_ARN` | ARN of SNS topic for notifications | Yes |

## Dependencies

```
boto3==1.34.11     # AWS SDK for Python
python-dotenv==1.0.0  # Environment variable management
```

## Testing

To test locally:
1. Set up AWS credentials
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables
4. Run: `python -c "import lambda_function; lambda_function.lambda_handler(None, None)"`

## Error Handling

The function handles these error cases:
- Cost Explorer API failures
- SNS publication errors
- Data processing issues
- Missing environment variables

## Logging

CloudWatch Logs capture:
- Function invocation
- Cost data retrieval
- Calculation results
- SNS notification status
- Error details

## Performance

- Timeout: 30 seconds
- Memory: 128 MB
- Average runtime: ~5 seconds
- API calls per execution: 2-3
