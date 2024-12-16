import sys
import os
import json
import subprocess
from datetime import datetime

# Import custom modules for specific tasks
from cos_bucket_manager import cos_client, list_and_manage_buckets
from toolchain_manager import list_toolchains
from scc_manager import list_scc_instances
from secrets_manager import list_secrets_manager_instances

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

    with open("./json_files/cos_bucket_requests.json", "a") as file:
        file.write(json.dumps(request_data) + "\n")

    print("\nRequest saved to cos_bucket_requests.json")

def request_credentials(service_name, environment, soc2_controls, pipeline):
    print("\nRequesting credentials or access details from IBM Service Team...")
    print("Please ensure you contact the relevant IBM Cloud team with the following details:")
    print(f"Service Name: {service_name}")
    print(f"Environment: {environment}")
    print(f"SOC2 Controls: {soc2_controls}")
    print(f"Pipeline: {pipeline}")
    print("\nSending request to IBM Service Team...")
    # Simulating a request (you can replace this with actual API calls or email triggers)
    print("Request sent successfully!")

def run_terraform_plan(service_name, environment, soc2_controls, ibm_api_key):
    print("\nChecking if Terraform initialization is needed...")

    # Set the required variables for Terraform
    terraform_vars = {
        "service_name": service_name,
        "environment": environment,
        "soc2_controls": soc2_controls,
        "ibm_api_key": ibm_api_key  # Adding IBM API key to terraform input
    }

    # Create a copy of the current environment and set the Terraform variables
    env = os.environ.copy()
    for var, value in terraform_vars.items():
        env[f"TF_VAR_{var}"] = value

    # Define the path to the Terraform scripts directory
    terraform_dir = "Terraform_Scripts"

    # Check if .terraform directory exists in the specified folder
    if not os.path.exists(os.path.join(terraform_dir, ".terraform")):
        print("\nRunning terraform init...")
        try:
            # Initialize Terraform in the correct directory
            init_result = subprocess.run(
                ["terraform", "init"],
                capture_output=True,
                text=True,
                check=True,
                cwd=terraform_dir,  # Change to the Terraform scripts directory
                env=env  # Pass the modified environment to subprocess
            )
            print("Terraform initialization completed.")
            print(init_result.stdout)
        except subprocess.CalledProcessError as e:
            print("Error running terraform init:")
            print(e.stderr)
            return
    else:
        print("\nTerraform is already initialized. Skipping terraform init...")

    try:
        # Run Terraform plan in the correct directory
        print("\nRunning terraform plan...")
        plan_result = subprocess.run(
            ["terraform", "plan"],
            capture_output=True,
            text=True,
            check=True,
            cwd=terraform_dir,  # Change to the Terraform scripts directory
            env=env  # Pass the modified environment to subprocess
        )
        print("Terraform plan executed successfully.")
        print(plan_result.stdout)

    except subprocess.CalledProcessError as e:
        print("Error running terraform plan:")
        print(e.stderr)

def main():
    pipeline = prompt_user()
    service_name, environment, soc2_controls = get_details()
    
    # Ask the user for the IBM Cloud API Key
    ibm_api_key = input("Enter your IBM Cloud API Key: ")

    # Print out the last 4 characters of the API key (for debugging purposes)
    print(f"\nIBM Cloud API Key provided: ********{ibm_api_key[-4:]}")

    save_request(service_name, environment, soc2_controls, pipeline)
    request_credentials(service_name, environment, soc2_controls, pipeline)

    # List and manage COS instances in the IBM Cloud account
    cos = cos_client(ibm_api_key)
    if cos:
        list_and_manage_buckets(cos, environment)

    # List toolchains in the IBM Cloud account
    # print("\nListing available toolchains:")
    # list_toolchains(ibm_api_key)

    # List SCC instances in the IBM Cloud account
    # print("\nListing SCC instances:")
    # list_scc_instances(ibm_api_key)

    # List Secrets Manager instances in the IBM Cloud account
    # print("\nListing Secrets Manager instances:")
    # list_secrets_manager_instances(ibm_api_key)

    # Uncomment the next line to run Terraform plan
    # run_terraform_plan(service_name, environment, soc2_controls, ibm_api_key)

if __name__ == "__main__":
    main()
