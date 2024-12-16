# Checking Permissions of an IBM Cloud API Key

To verify the permissions associated with an IBM Cloud API key and determine if it can perform specific tasks (e.g., creating a COS bucket, managing Secrets Manager, or configuring a toolchain), follow these steps:

---

## 1. Check API Key Details
Use the following command to display information about the API key, including its associated service ID or user:

```bash
ibmcloud iam api-key-details <your_api_key>
```

## 2. Check Permissions of the Service ID or User
If the API key is linked to a Service ID, find its permissions by listing its access policies:

# For Service IDs:
```bash
ibmcloud iam service-id <SERVICE_ID>
ibmcloud iam policies --service-id <SERVICE_ID>
```

# For Users:
```bash
ibmcloud iam policies --user-id <USER_ID>
```


## 3. Verify Permissions for Specific Resources
To check if the API key has permissions to create specific resources (like a COS bucket, Secrets Manager instance, or toolchain), identify the required IAM roles for those services:
```bash 
ibmcloud iam policy <POLICY_ID>
```

## 4. Automate with Terraform
To incorporate this validation into Terraform:

Use an external data source to execute the CLI commands via a script.
Parse the output to determine if the API key has the necessary permissions.

```bash
#!/bin/bash
# Login with the API key
ibmcloud login --apikey $API_KEY

# Retrieve the Service ID
SERVICE_ID=$(ibmcloud iam api-key-details $API_KEY | grep "Service ID" | awk '{print $3}')

# Fetch the policies for the Service ID
ibmcloud iam policies --service-id $SERVICE_ID > policies.json

# Check for permissions
if grep -q "cloud-object-storage" policies.json; then
    echo "COS permissions found"
else
    echo "COS permissions missing"
fi
```
