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

- AWS CLI configured with appropriate credentials
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
├── terraform/
│   ├── main.tf              # Main Terraform configuration
│   ├── variables.tf         # Input variables
│   ├── terraform.tfvars     # Variable values
│   └── modules/
│       └── lambda-cost-alert/
│           ├── main.tf      # Lambda module configuration
│           ├── variables.tf  # Module variables
│           ├── outputs.tf   # Module outputs
│           └── src/         # Lambda function source code
│               ├── lambda_function.py
│               ├── requirements.txt
│               └── README.md
```

## Deployment

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/aws-cost-alert.git
   cd aws-cost-alert/terraform
   ```

2. Update variables in `terraform.tfvars`:
   ```hcl
   email_endpoint = "your.email@example.com"
   ```

3. Initialize Terraform:
   ```bash
   terraform init
   ```

4. Deploy:
   ```bash
   terraform apply
   ```

5. Confirm your email subscription when you receive the AWS notification.

## Configuration

### Terraform Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `project_name` | Name prefix for AWS resources | aws-cost-alert |
| `aws_region` | AWS region for deployment | us-east-1 |
| `email_endpoint` | Email to receive alerts | (Required) |
| `schedule_expression` | CloudWatch schedule | cron(0 13 * * ? *) |

### Cost Alert Settings

The Lambda function provides:
- Daily cost comparison
- Monthly forecasting
- Trend analysis
- Daily run rate calculation

## Monitoring

- CloudWatch Logs for Lambda function output
- SNS delivery status
- Cost Explorer API metrics

## Cleanup

To remove all resources:
```bash
terraform destroy
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
