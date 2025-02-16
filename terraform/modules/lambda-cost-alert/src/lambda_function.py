import os
import json
import boto3
from datetime import datetime, timedelta
from decimal import Decimal
import calendar

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super(DecimalEncoder, self).default(obj)

def get_cost_data():
    client = boto3.client('ce')
    
    # Get current date
    now = datetime.now()
    end_date = now.strftime('%Y-%m-%d')
    
    # Get first day of current month
    first_day = now.replace(day=1)
    first_day_str = first_day.strftime('%Y-%m-%d')
    
    # Get yesterday's date for daily cost
    yesterday = (now - timedelta(days=1)).strftime('%Y-%m-%d')
    day_before = (now - timedelta(days=2)).strftime('%Y-%m-%d')
    
    # Get monthly cost (from start of month until now)
    monthly_response = client.get_cost_and_usage(
        TimePeriod={
            'Start': first_day_str,
            'End': end_date
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost']
    )
    
    # Get daily cost (yesterday's cost)
    daily_response = client.get_cost_and_usage(
        TimePeriod={
            'Start': day_before,
            'End': end_date
        },
        Granularity='DAILY',
        Metrics=['UnblendedCost']
    )
    
    # Get month-to-date cost
    current_month_cost = monthly_response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount']
    
    # Get yesterday's cost
    daily_cost = daily_response['ResultsByTime'][-1]['Total']['UnblendedCost']['Amount']
    
    # Calculate daily average for current month
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    days_so_far = now.day
    daily_avg = float(current_month_cost) / days_so_far
    
    # Get cost forecast for the full month
    forecast = client.get_cost_forecast(
        TimePeriod={
            'Start': end_date,
            'End': (first_day + timedelta(days=days_in_month)).strftime('%Y-%m-%d')
        },
        Metric='UNBLENDED_COST',
        Granularity='MONTHLY'
    )
    
    forecast_cost = forecast['Total']['Amount']
    
    # Calculate more accurate forecast based on current run rate
    daily_run_rate = float(current_month_cost) / days_so_far
    days_remaining = days_in_month - days_so_far
    projected_additional_cost = daily_run_rate * days_remaining
    adjusted_forecast = float(current_month_cost) + projected_additional_cost
    
    return {
        'current_month_cost': current_month_cost,
        'daily_cost': daily_cost,
        'daily_average': str(round(daily_avg, 2)),
        'forecast_cost': str(round(adjusted_forecast, 2)),  # Use adjusted forecast
        'aws_forecast': forecast_cost,  # Keep AWS forecast for comparison
        'days_in_month': days_in_month,
        'days_so_far': days_so_far,
        'daily_run_rate': str(round(daily_run_rate, 2))
    }

def send_sns_notification(cost_data):
    sns = boto3.client('sns')
    
    # Calculate the percentage change in daily cost vs daily average
    daily_cost = float(cost_data['daily_cost'])
    daily_avg = float(cost_data['daily_average'])
    current_month = float(cost_data['current_month_cost'])
    forecast = float(cost_data['forecast_cost'])
    daily_run_rate = float(cost_data['daily_run_rate'])
    
    daily_change = ((daily_cost - daily_avg) / daily_avg) * 100 if daily_avg > 0 else 0
    forecast_change = ((forecast - current_month) / current_month) * 100 if current_month > 0 else 0
    
    daily_trend = "📈" if daily_cost > daily_avg else "📉"
    forecast_trend = "📈" if forecast > current_month else "📉"
    
    message = f"""📊 AWS Cost Alert Summary
----------------------------------------

💰 Current Month's Cost: ${current_month:.2f} USD
📅 Days: {cost_data['days_so_far']}/{cost_data['days_in_month']}

Daily Analysis:
• Yesterday's Cost: ${daily_cost:.2f} USD {daily_trend}
• Daily Average: ${daily_avg:.2f} USD
• Current Run Rate: ${daily_run_rate} USD/day
• Daily Trend: {'+' if daily_change > 0 else ''}{daily_change:.1f}%

Monthly Projection (Based on Current Run Rate):
• Projected End Cost: ${forecast:.2f} USD {forecast_trend}
• Additional Cost: ${(forecast - current_month):.2f} USD
• Change: {'+' if forecast_change > 0 else ''}{forecast_change:.1f}%

⏰ Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
----------------------------------------
View Details: https://console.aws.amazon.com/cost-management/home"""

    sns.publish(
        TopicArn=os.environ['SNS_TOPIC_ARN'],
        Subject=f'AWS Cost Alert - ${current_month:.2f} MTD | Run Rate: ${daily_run_rate}/day',
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
