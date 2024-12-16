terraform {
  required_providers {
    ibm = {
      source  = "ibm-cloud/ibm"
      version = "~> 1.50.0"
    }
  }
}

# Declare the variable for the IBM Cloud API key
variable "ibm_api_key" {
  description = "API key for IBM Cloud authentication"
  type        = string
}

# Configure the IBM provider using the API key
provider "ibm" {
  ibmcloud_api_key = var.ibm_api_key
}

# Data source to fetch the IAM access token details
data "ibm_iam_auth_token" "token" {}

# Data source to fetch the user's account ID
data "ibm_iam_account_settings" "account_settings" {}

# Output the user's account ID
output "account_id" {
  value = data.ibm_iam_account_settings.account_settings.account_id
}

# Output the IAM access token details (for debugging)
output "iam_access_token_details" {
  value     = data.ibm_iam_auth_token.token
  # sensitive = true
}
