import unittest
from unittest.mock import patch, MagicMock
from moto import mock_sns, mock_ce
import boto3
import json
from lambda_function import lambda_handler, get_cost_data, send_sns_notification

class TestAWSCostAlert(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.topic_arn = 'arn:aws:sns:us-east-1:123456789012:test-topic'
        self.patcher = patch.dict('os.environ', {'SNS_TOPIC_ARN': self.topic_arn})
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    @mock_ce
    def test_get_cost_data(self):
        """Test getting cost data from AWS Cost Explorer"""
        # Mock CE client responses
        with patch('boto3.client') as mock_client:
            mock_ce = MagicMock()
            mock_ce.get_cost_and_usage.return_value = {
                'ResultsByTime': [{
                    'Total': {
                        'UnblendedCost': {
                            'Amount': '100.00'
                        }
                    }
                }]
            }
            mock_ce.get_cost_forecast.return_value = {
                'Total': {
                    'Amount': '120.00'
                }
            }
            mock_client.return_value = mock_ce

            cost_data = get_cost_data()
            
            self.assertEqual(cost_data['current_cost'], '100.00')
            self.assertEqual(cost_data['forecast_cost'], '120.00')
            
            # Verify CE client was called correctly
            mock_client.assert_called_with('ce')

    def test_send_sns_notification(self):
        """Test sending SNS notification"""
        mock_sns = MagicMock()
        
        with patch('boto3.client', return_value=mock_sns):
            cost_data = {
                'current_cost': '100.00',
                'forecast_cost': '120.00'
            }
            
            # Test the notification sending
            send_sns_notification(cost_data)
            
            # Verify SNS publish was called with correct parameters
            mock_sns.publish.assert_called_once()
            call_kwargs = mock_sns.publish.call_args.kwargs
            
            self.assertEqual(call_kwargs['TopicArn'], self.topic_arn)
            self.assertIn('AWS Cost Alert Summary', call_kwargs['Message'])
            self.assertIn('$100.00 USD', call_kwargs['Message'])
            self.assertIn('$120.00 USD', call_kwargs['Message'])
            self.assertEqual(call_kwargs['Subject'], 'AWS Cost Alert - $100.00 (📈)')

    def test_lambda_handler(self):
        """Test the main lambda handler"""
        with patch('lambda_function.get_cost_data') as mock_get_cost:
            with patch('lambda_function.send_sns_notification') as mock_send:
                # Mock cost data
                mock_cost_data = {
                    'current_cost': '100.00',
                    'forecast_cost': '120.00'
                }
                mock_get_cost.return_value = mock_cost_data
                
                # Test lambda handler
                result = lambda_handler({}, {})
                
                # Verify response
                self.assertEqual(result['statusCode'], 200)
                body = json.loads(result['body'])
                self.assertEqual(body['message'], 'Cost alert sent successfully')
                self.assertEqual(body['data'], mock_cost_data)
                
                # Verify functions were called
                mock_get_cost.assert_called_once()
                mock_send.assert_called_once_with(mock_cost_data)

    def test_lambda_handler_error(self):
        """Test lambda handler error handling"""
        with patch('lambda_function.get_cost_data', side_effect=Exception('Test error')):
            result = lambda_handler({}, {})
            
            self.assertEqual(result['statusCode'], 500)
            body = json.loads(result['body'])
            self.assertEqual(body['message'], 'Error: Test error')

if __name__ == '__main__':
    unittest.main()
