import json
import ibm_boto3
from ibm_botocore.client import Config
from ibm_botocore.exceptions import NoCredentialsError


def cos_client(ibm_api_key):
    """Create and return the COS client using provided API key."""
    try:
        with open("./json_files/cos-service-cred.json", "r") as file:
            cos_creds = json.load(file)
        
        service_instance_id = cos_creds.get("resource_instance_id")
        endpoint_url = "https://s3.us-south.cloud-object-storage.appdomain.cloud"  # Replace with your endpoint

        cos = ibm_boto3.client(
            "s3",
            ibm_api_key_id=ibm_api_key,
            ibm_service_instance_id=service_instance_id,
            config=Config(signature_version="oauth"),
            endpoint_url=endpoint_url
        )

        return cos
    except NoCredentialsError:
        print("IBM Cloud API key or credentials are missing. Please provide valid credentials.")
        return None
    except Exception as e:
        print(f"Error in creating COS client: {e}")
        return None


def naming_convention(environment):
    """Generate bucket name based on environment."""
    return f"terraform-{environment}-bucket"


def list_and_manage_buckets(cos, environment):
    """List and manage buckets in COS."""
    try:
        # List all buckets
        response = cos.list_buckets()
        buckets = response.get("Buckets", [])
        for bucket in buckets:
            print(f" - {bucket['Name']}")
        
        # Define the target bucket name based on the naming convention
        target_bucket_name = naming_convention(environment)
        print(f"\nTarget Bucket Name: {target_bucket_name}\n")
        
        # Check if a bucket with the naming convention exists
        matching_buckets = [
            bucket["Name"] for bucket in buckets if target_bucket_name in bucket["Name"]
        ]

        if matching_buckets:
            print("Matching Buckets:")
            for bucket in matching_buckets:
                print(f" - {bucket}")
        else:
            print(f"No buckets found with the naming convention '{target_bucket_name}'.")
            print("Creating the target bucket...")
            
            # Create the bucket
            cos.create_bucket(
                Bucket=target_bucket_name,
                CreateBucketConfiguration={"LocationConstraint": "us-south"}
            )
            print(f"Bucket '{target_bucket_name}' created successfully!")
    
    except Exception as e:
        print("Error managing buckets: ", e)
