# AWS Cost Alert System

A serverless AWS cost monitoring system that sends daily cost alerts and forecasts via email.

## Features

- 📊 Daily AWS cost monitoring
- 📈 Cost trend analysis and forecasting
- 📧 Email notifications via SNS
- ⚡ Serverless architecture using AWS Lambda
- 🔄 Daily automated runs (20:00 Bangkok time)
- 🛠 Infrastructure as Code using Terraform

## Architecture

```
┌─────────────┐    ┌──────────┐    ┌─────────┐    ┌──────────┐
│ CloudWatch  │───>│  Lambda  │───>│   SNS   │───>│  Email   │
│  Events     │    │ Function │    │  Topic  │    │ Inbox    │
└─────────────┘    └──────────┘    └─────────┘    └──────────┘
                         │
                         v
                   ┌──────────┐
                   │   Cost   │
                   │ Explorer │
                   └──────────┘
```

## Prerequisites

- AWS CLI configured with appropriate permissions
- Terraform >= 1.0
- Python 3.9+
- AWS account with permissions for:
  - Lambda
  - CloudWatch Events
  - SNS
  - Cost Explorer
  - IAM

## Project Structure

```
aws-cost-alert/
├── README.md               # Project documentation
├── terraform/             # Infrastructure as Code
│   ├── main.tf           # Main Terraform configuration
│   ├── variables.tf      # Input variables
│   ├── terraform.tfvars  # Variable values
│   └── modules/
│       └── lambda-cost-alert/
│           ├── main.tf   # Lambda module configuration
│           ├── variables.tf
│           ├── outputs.tf
│           └── src/      # Lambda function source code
│               ├── lambda_function.py
│               ├── requirements.txt
│               └── README.md  # Technical documentation
```

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/aws-cost-alert.git
   cd aws-cost-alert
   ```

2. Update Terraform variables:
   ```bash
   cd terraform
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your email
   ```

3. Deploy the infrastructure:
   ```bash
   terraform init
   terraform apply
   ```

4. Confirm your email subscription when you receive the AWS notification.

## Deployment Methods

### 1. Using Terraform (Recommended)

The Terraform deployment:
- Creates all required AWS resources
- Sets up proper IAM roles and permissions
- Configures CloudWatch scheduling
- Manages Lambda deployment package
- Sets up SNS notifications

See [terraform/README.md](terraform/README.md) for detailed Terraform configuration.

### 2. Manual Deployment

You can also deploy manually using the AWS Console or CLI:

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r terraform/modules/lambda-cost-alert/src/requirements.txt
   ```

2. Create AWS resources:
   ```bash
   # Create SNS Topic
   aws sns create-topic --name aws-cost-alert

   # Create Lambda function (see deploy.sh for full script)
   aws lambda create-function ...
   ```

See [src/README.md](terraform/modules/lambda-cost-alert/src/README.md) for technical details.

## Cost Analysis

### AWS Service Costs
- Lambda: Free tier includes 1M requests/month
- SNS: Free tier includes 1M publishes/month
- Cost Explorer: $0.01 per API request
- CloudWatch: Free tier includes 10 metrics/month

### Estimated Monthly Cost
- Total: < $1/month for daily alerts
- Main cost factor: Cost Explorer API calls

## Customization

The system can be customized by:
1. Modifying the Lambda function code
2. Adjusting the CloudWatch schedule
3. Changing the cost calculation logic
4. Customizing email templates

See technical documentation for details.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Make your changes
4. Run tests: `cd terraform/modules/lambda-cost-alert/src && python -m pytest`
5. Submit a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- AWS Cost Explorer API
- Terraform AWS Provider
- Python Boto3 SDK
