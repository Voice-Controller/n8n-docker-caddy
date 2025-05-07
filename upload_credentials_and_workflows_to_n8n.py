import requests
import json
import os
import argparse

"""
This script uploads credentials and workflows to an n8n instance.

Prerequisites:
- Python 3.x
- requests library (pip install requests)
- Environment variable N8N_API_KEY set with your n8n API key
- credentials.json and workflows.json files in the same directory as this script
  (These can be generated using backup_credentials_and_workflows.sh)

Usage:
1. Set your n8n API key as an environment variable:
   export N8N_API_KEY='your-api-key-here'

2. Run the script:
   python upload_credentials_and_workflows_to_n8n.py --credentials ./backups/credentials.json --workflows ./backups/workflows.json

The script will:
- Ask if you want to wipe existing workflows
- If yes, delete all existing workflows
- Import credentials from credentials.json
- Import workflows from workflows.json

Note: 
- Make sure your API key has sufficient permissions to perform these operations.
- The n8n REST API does not allow listing credentials, so we cannot wipe existing credentials.
"""

N8N_URL = "https://voicecontroller.app.n8n.cloud"
API_KEY = os.environ.get('N8N_API_KEY')

if not API_KEY:
    raise ValueError("N8N_API_KEY environment variable is not set")

HEADERS = {
    "X-N8N-API-KEY": API_KEY,
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def wipe_existing_workflows():
    """Wipes all existing workflows from the n8n instance"""
    print("\nFetching existing workflows...")
    
    # First get all workflows
    response = requests.get(f"{N8N_URL}/api/v1/workflows", headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to get workflows: {response.status_code}")
        print(f"Response body: {response.text}")
        print("Please check that your API key has sufficient permissions")
        print(f"Using N8N URL: {N8N_URL}")
        return
        
    workflows = response.json()
    if not isinstance(workflows, dict) or 'data' not in workflows:
        print("Unexpected response format when getting workflows")
        print(f"Response: {workflows}")
        return
        
    # First deactivate all active workflows
    for workflow in workflows['data']:
        if workflow.get('active'):
            deactivate_response = requests.post(
                f"{N8N_URL}/api/v1/workflows/{workflow['id']}/deactivate",
                headers=HEADERS
            )
            if deactivate_response.status_code != 200:
                print(f"Failed to deactivate workflow {workflow.get('name')}: {deactivate_response.status_code}")
    
    # Then delete each workflow
    for workflow in workflows['data']:
        if 'id' not in workflow:
            print(f"Workflow missing ID: {workflow}")
            continue
            
        delete_response = requests.delete(
            f"{N8N_URL}/api/v1/workflows/{workflow['id']}", 
            headers=HEADERS
        )
        
        if delete_response.status_code == 200:
            print(f"Successfully deleted workflow {workflow.get('name')} (ID: {workflow['id']})")
        else:
            print(f"Failed to delete workflow {workflow.get('name')} (ID: {workflow['id']}): {delete_response.status_code}")
            print(delete_response.text)

def import_credentials(credentials_path):
    with open(credentials_path) as f:
        credentials_data = json.load(f)
        
    for credential in credentials_data:
        # Remove read-only fields and additional properties that aren't allowed
        excluded_fields = ['id', 'createdAt', 'updatedAt']
        credential_data = {k: credential[k] for k in credential if k not in excluded_fields}
        
        # Remove nested fields that aren't allowed in data property
        if 'data' in credential_data:
            excluded_data_fields = [
                'grantType', 'authUrl', 'accessTokenUrl', 'scope',
                'authQueryParameters', 'authentication'
            ]
            credential_data['data'] = {
                k: credential_data['data'][k] 
                for k in credential_data['data'] 
                if k not in excluded_data_fields
            }
            
        response = requests.post(
            f"{N8N_URL}/api/v1/credentials",
            headers=HEADERS,
            json=credential_data
        )
        print(f"Credential import response for {credential.get('name')}:", response.status_code)
        if response.status_code != 200:
            print(response.text)

def import_workflows(workflows_path):
    with open(workflows_path) as f:
        workflows_data = json.load(f)
        
    for workflow in workflows_data:
        # Remove additional properties that aren't allowed
        allowed_fields = ['name', 'nodes', 'connections', 'settings']  # Removed 'tags' as it's read-only
        workflow_data = {k: workflow[k] for k in allowed_fields if k in workflow}
        
        response = requests.post(
            f"{N8N_URL}/api/v1/workflows",
            headers=HEADERS,
            json=workflow_data
        )
        print(f"Workflow import response for {workflow.get('name')}:", response.status_code)
        if response.status_code != 200:
            print(response.text)

if __name__ == "__main__":
    should_wipe = input("Do you want to wipe existing workflows? (y/N): ").lower() == 'y'
    
    if should_wipe:
        print("Wiping existing workflows...")
        wipe_existing_workflows()

    parser = argparse.ArgumentParser(description='Import n8n credentials and workflows')
    parser.add_argument('--credentials', default='credentials.json',
                      help='Path to credentials JSON file (default: credentials.json)')
    parser.add_argument('--workflows', default='workflows.json', 
                      help='Path to workflows JSON file (default: workflows.json)')
    args = parser.parse_args()

    print("Importing credentials...")
    import_credentials(args.credentials)
    print("Importing workflows...")
    import_workflows(args.workflows)
