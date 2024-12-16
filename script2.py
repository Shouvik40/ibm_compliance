import sys
import json
import subprocess
import os
from datetime import datetime

def prompt_user():
    print("Select SCC Dashboard Pipeline Option:")
    print("1. Data Collection Pipeline")
    print("2. Data Transformation Pipeline")
    print("3. End-To-End Pipeline")

    pipeline_choice = input("Enter your choice (1/2/3): ")
    pipelines = {
        "1": "Data Collection Pipeline",
        "2": "Data Transformation Pipeline",
        "3": "End-To-End Pipeline"
    }

    pipeline = pipelines.get(pipeline_choice)
    if not pipeline:
        print("Invalid choice. Exiting.")
        sys.exit(1)
    print(f"You selected: {pipeline}")
    return pipeline

def get_details():
    service_name = input("Enter the Service Name: ")
    environment = input("Enter the Environment (e.g., dev, test, prod): ")
    soc2_controls = input("Enter the SOC2 Controls to be fetched (comma-separated): ")

    print("\nDetails provided:")
    print(f"Service Name: {service_name}")
    print(f"Environment: {environment}")
    print(f"SOC2 Controls: {soc2_controls}")
    return service_name, environment, soc2_controls

def save_request(service_name, environment, soc2_controls, pipeline):
    request_data = {
        "timestamp": datetime.now().isoformat(),
        "service_name": service_name,
        "environment": environment,
        "soc2_controls": soc2_controls,
        "pipeline": pipeline
    }
    with open("scc_requests.json", "a") as file:
        file.write(json.dumps(request_data) + "\n")
    print("\nRequest saved to scc_requests.json")

def list_cos_buckets(cos_client):
    try:
        response = cos_client.list_buckets()
        buckets = response.get('Buckets', [])
        print("\nAvailable COS Buckets:")
        for bucket in buckets:
            print(f"- {bucket['Name']}")
        return buckets
    except NoCredentialsError:
        print("Credentials not available for listing COS buckets.")
        return []

def check_existing_bucket(buckets, naming_pattern):
    print("\nChecking for existing buckets matching naming convention...")
    for bucket in buckets:
        if naming_pattern in bucket['Name']:
            print(f"Matching bucket found: {bucket['Name']}")
            return bucket['Name']
    print("No matching bucket found.")
    return None

def create_cos_bucket(cos_client, bucket_name):
    print(f"\nCreating a new COS bucket: {bucket_name}")
    try:
        cos_client.create_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} created successfully.")
        return bucket_name
    except Exception as e:
        print(f"Error creating bucket: {str(e)}")
        sys.exit(1)

def run_terraform_plan(service_name, environment, soc2_controls, ibm_api_key):
    print("\nChecking if Terraform initialization is needed...")
    terraform_vars = {
        "service_name": service_name,
        "environment": environment,
        "soc2_controls": soc2_controls,
        "ibm_api_key": ibm_api_key
    }

    env = os.environ.copy()
    for var, value in terraform_vars.items():
        env[f"TF_VAR_{var}"] = value

    terraform_dir = "Terraform_Scripts"
    if not os.path.exists(os.path.join(terraform_dir, ".terraform")):
        print("\nRunning terraform init...")
        subprocess.run(
            ["terraform", "init"],
            cwd=terraform_dir,
            env=env,
            check=True
        )
    else:
        print("Terraform is already initialized.")

    print("\nRunning terraform plan...")
    subprocess.run(
        ["terraform", "plan"],
        cwd=terraform_dir,
        env=env,
        check=True
    )

def main():
    pipeline = prompt_user()
    service_name, environment, soc2_controls = get_details()
    ibm_api_key = input("Enter your IBM Cloud API Key: ")

    print(f"\nIBM Cloud API Key provided: ********{ibm_api_key[-4:]}")
    save_request(service_name, environment, soc2_controls, pipeline)

    # Initialize IBM COS client
    cos_client = client(
        's3',
        ibm_api_key_id=ibm_api_key,
        endpoint_url="https://s3.us.cloud-object-storage.appdomain.cloud"
    )

    # List COS buckets
    buckets = list_cos_buckets(cos_client)

    # Check for existing buckets matching naming convention
    naming_pattern = f"{service_name}-{environment}-cos"
    existing_bucket = check_existing_bucket(buckets, naming_pattern)

    if existing_bucket:
        print(f"Using existing bucket: {existing_bucket}")
    else:
        # Create new bucket if none match
        bucket_name = f"{naming_pattern}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        create_cos_bucket(cos_client, bucket_name)

    # Run Terraform plan
    run_terraform_plan(service_name, environment, soc2_controls, ibm_api_key)

if __name__ == "__main__":
    main()
