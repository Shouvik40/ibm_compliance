from ibm_secrets_manager_sdk.secrets_manager_v2 import SecretsManagerV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException

def list_secrets_manager_instances(api_key):
    try:
        print("\nListing all Secrets Manager instances...")

        # Authenticate and create the Secrets Manager client
        authenticator = IAMAuthenticator(api_key)
        secrets_manager = SecretsManagerV2(authenticator=authenticator)
        secrets_manager.set_service_url('https://api.us-south.devops.cloud.ibm.com/toolchain/v2')  # Replace <region> with your actual region

        # Fetch the list of secrets
        response = secrets_manager.list_secrets().get_result()
        print("response")
        # Process and display the list of secrets
        if 'resources' in response:
            secrets_instances = response['resources']
            if secrets_instances:
                for secret in secrets_instances:
                    print(f"Secret Name: {secret.get('name', 'Unnamed')} - Type: {secret.get('secret_type', 'Unknown')}")
            else:
                print("No secrets found in the Secrets Manager.")
        else:
            print("Unexpected response structure received.")
    except ApiException as ex:
        print(f"Failed to list Secrets Manager instances: {ex}")
