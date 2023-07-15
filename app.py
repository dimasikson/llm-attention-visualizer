from flask import Flask, render_template, request
import requests
import json

from azureml.core import Workspace
from azureml.core.authentication import ServicePrincipalAuthentication


app = Flask(__name__)


# Load environment variables
with open("./summarize/environ.json") as f:
    environment_variables = json.load(f)
    tenant_id = environment_variables["tenant"]
    resource_group = environment_variables["resource_group"]
    subscription_id = environment_variables["subscription_id"]
    service_principal_app_id = environment_variables["service_principal_app_id"]
    service_principal_pwd = environment_variables["service_principal_pwd"]
    azureml_workspace_name = environment_variables["azureml_workspace_name"]
    service_name = environment_variables["summarize_service_name"]

# Authenticate with service principal
service_principal = ServicePrincipalAuthentication(
    tenant_id=tenant_id,
    service_principal_id=service_principal_app_id,
    service_principal_password=service_principal_pwd
)

# Connect to workspace
workspace = Workspace(
    subscription_id=subscription_id,
    resource_group=resource_group,
    workspace_name=azureml_workspace_name,
    auth=service_principal
)

# Get key vault
key_vault = workspace.get_default_keyvault()

# Get URL from key vault
llm_api_url = key_vault.get_secret(name=f"{service_name}-URL")


def send_request(name, body):
    return requests.post(
        url = llm_api_url,
        data = json.dumps({ "name": name, "body": body }),
        headers={"Content-Type": "application/json"},
    )


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/encode", methods=["POST"])
def encode():
    body = request.get_json()    
    response = send_request(name = "encode", body = body)
    return response.json()


@app.route("/decode", methods=["POST"])
def decode():
    body = request.get_json()    
    response = send_request(name = "decode", body = body)
    return response.json()


@app.route("/generate", methods=["POST"])
def generate():
    body = request.get_json()    
    response = send_request(name = "generate", body = body)
    return response.json()


if __name__ == "__main__":
    app.run(debug=True)
