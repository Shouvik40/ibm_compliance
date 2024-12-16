import sys
import json
from ibm_cloud_sdk_core import ApiException
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_platform_services import ToolchainV2

# Function to authenticate and create a toolchain client
def create_toolchain_client(api_key):
    authenticator = IAMAuthenticator(api_key)
    toolchain_service = ToolchainV2(authenticator=authenticator)
    toolchain_service.set_service_url('https://api.us-south.devops.cloud.ibm.com')  # Replace with the correct URL for the region
    return toolchain_service

# Function to list all toolchains in a given region
def list_toolchains(api_key, region):
    try:
        toolchain_service = create_toolchain_client(api_key)
        
        # Fetch toolchains in the specified region
        response = toolchain_service.list_toolchains(limit=50).get_result()

        print(f"Toolchains in region {region}:")
        if 'toolchains' in response:
            for toolchain in response['toolchains']:
                print(f"- Toolchain Name: {toolchain['name']}")
                print(f"  Toolchain ID: {toolchain['id']}")
                print(f"  Created at: {toolchain['created_at']}")
                print(f"  Region: {toolchain['region']}\n")
        else:
            print("No toolchains found.")

    except ApiException as e:
        print(f"Error occurred: {e.message}")
        sys.exit(1)

# Main function
def main():
    # Ask for the API key and region
    api_key = input("Enter your IBM Cloud API Key: ")
    region = input("Enter the region (e.g., us-south, eu-de): ")

    # List toolchains in the specified region
    list_toolchains(api_key, region)

if __name__ == "__main__":
    main()
