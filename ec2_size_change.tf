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
  region = "ap-south-1" # Replace with your desired AWS region
}

# Define the EC2 instance resource
resource "aws_instance" "example" {
  ami                    = "ami-080b1a55a0ad28c02" # Replace with your desired AMI ID
  instance_type          = "t2.micro"
  key_name               = "mumbai_region_key" # Replace with your key pair name
  tags = {
    Name = "t2-micro-instance"
  }
  # Add other configurations as needed (e.g., subnet_id, security_group_ids)
}
