import os
import json
import boto3
from datetime import datetime, timedelta
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super(DecimalEncoder, self).default(obj)

def get_cost_data():
    client = boto3.client('ce')
    
    # Get current date and format it
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # Get current month's cost
    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost']
    )
    
    current_cost = response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']
    
    # Get cost forecast for the next month
    forecast = client.get_cost_forecast(
        TimePeriod={
            'Start': end_date,
            'End': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        },
        Metric='UNBLENDED_COST',
        Granularity='MONTHLY'
    )
    
    forecast_cost = forecast['Total']['Amount']
    
    return {
        'current_cost': current_cost,
        'forecast_cost': forecast_cost
    }

def send_sns_notification(cost_data):
    sns = boto3.client('sns')
    
    # Calculate the percentage change in forecast vs current
    current_cost = float(cost_data['current_cost'])
    forecast_cost = float(cost_data['forecast_cost'])
    percentage_change = ((forecast_cost - current_cost) / current_cost) * 100
    trend_indicator = "📈" if percentage_change > 0 else "📉"
    
    message = f"""📊 AWS Cost Alert Summary
----------------------------------------

💰 Current Month's Cost: ${current_cost:.2f} USD
🔮 Forecasted Cost (Next 30 days): ${forecast_cost:.2f} USD {trend_indicator}
📊 Trend: {'+' if percentage_change > 0 else ''}{percentage_change:.1f}%

Cost Breakdown:
----------------------------------------
• Monthly Run Rate: ${(current_cost/30):.2f} USD per day
• Projected Monthly Total: ${forecast_cost:.2f} USD

⏰ Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Note: This is an automated cost monitoring alert. For detailed 
cost analysis, please visit AWS Cost Explorer dashboard.
----------------------------------------
To manage these notifications or view detailed costs:
https://console.aws.amazon.com/cost-management/home"""

    sns.publish(
        TopicArn=os.environ['SNS_TOPIC_ARN'],
        Subject=f'AWS Cost Alert - ${current_cost:.2f} ({trend_indicator})',
        Message=message
    )

def lambda_handler(event, context):
    try:
        # Get cost data
        cost_data = get_cost_data()
        
        # Send notification
        send_sns_notification(cost_data)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Cost alert sent successfully',
                'data': cost_data
            }, cls=DecimalEncoder)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error: {str(e)}'
            })
        }
