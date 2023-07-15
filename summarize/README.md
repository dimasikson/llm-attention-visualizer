How to deploy this as a managed endpoint on Azure ML:
0. `pip install azureml-sdk`
1. Create a new Azure ML workspace, inside of a resource group
2. Create a service principal, and give it contributor access to the resource group
3. Create a file called `environ.json` in this directory. It should look like below, but with your own values:

```json
{   
    "tenant": "...", // This is the tenant ID of the Azure AD tenant that the service principal is in
    "resource_group": "...", // The name of the resource group that the Azure ML workspace is in
    "subscription_id": "...", // The subscription ID of the Azure subscription that the resource group is in
    "service_principal_app_id": "...", // The app ID of the service principal
    "service_principal_pwd": "...", // The pwd of the service principal
    "azureml_workspace_name": "...", // The name of the Azure ML workspace
    "summarize_service_name": "..." // The name of the service that you want to deploy
}
```

4. Run `python deploy.py` to deploy the model

**NOTE:** You have to delete the endpoint every time you want to redeploy it. Something to work on in the future.

How to run it:

```python
import requests
import json

# The URL of the endpoint
url = "http://<your-endpoint-url>/api/v1/service/<your-endpoint-name>/score"

# The data
data = json.dumps({
    "name": "encode",
    "body": {
        "text": "This is a test sentence"
    }
})

# The headers
headers = {"Content-Type": "application/json"}

# Send the request
response = requests.post(url, data=data, headers=headers)

# Print the response
print(response.json())
```

