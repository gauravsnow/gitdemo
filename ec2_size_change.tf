# Configure the AWS provider
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"  # Use the latest version
    }
  }
}

provider "aws" {
  region = "ap-northeast-3" # Replace with your desired AWS region
}

# Define the EC2 instance resource
resource "aws_instance" "example" {
  ami                    = "ami-08ea1604ee9ff115d" # Replace with your desired AMI ID
  instance_type          = "t2.micro"
  key_name               = "Osaka_ec2_deployment" # Replace with your key pair name
  tags = {
    Name = "t2-micro-instance"
  }
  # Add other configurations as needed (e.g., subnet_id, security_group_ids)
}
