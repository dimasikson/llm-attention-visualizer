import json
from datetime import datetime

from azureml.core import Environment
from azureml.core import Workspace
from azureml.core.model import Model
from azureml.core.model import InferenceConfig
from azureml.core.webservice import AciWebservice
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.authentication import ServicePrincipalAuthentication


ENTRY_SCRIPT = "app.py"
SOURCE_DIRECTORY = "."
ENVIRONMENT_NAME = "myenv"
ENVIRON_FILE = "./environ.json"
REQUIREMENTS_FILE = "./requirements.txt"
CPU_CORES = 2
MEMORY_GB = 4


if __name__ == "__main__":

    # Load environment variables
    with open(ENVIRON_FILE) as f:
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
        service_principal_pwd=service_principal_pwd
    )

    print(datetime.now(), "Service principal authenticated.")

    # Connect to workspace
    workspace = Workspace(
        subscription_id=subscription_id,
        resource_group=resource_group,
        workspace_name=azureml_workspace_name,
        auth=service_principal
    )

    print(datetime.now(), "Connected to workspace.")

    # Get key vault
    key_vault = workspace.get_default_keyvault()

    print(datetime.now(), "Got key vault.")

    # Create environment + conda dependencies
    environment = Environment(name = ENVIRONMENT_NAME)
    conda_dependencies = CondaDependencies()

    # Add packages from requirements.txt to conda dependencies
    with open(REQUIREMENTS_FILE) as f:
        for line in f:

            # Add package to conda dependencies
            conda_dependencies.add_pip_package(line.strip())

            print(datetime.now(), "Added package:", line.strip())

    # Assign conda dependencies to environment
    environment.python.conda_dependencies = conda_dependencies

    print(datetime.now(), "Created environment.")

    # Inference config
    inference_config = InferenceConfig(
        environment=environment,
        entry_script=ENTRY_SCRIPT,
        source_directory=SOURCE_DIRECTORY,
    )

    print(datetime.now(), "Created inference config.")

    # ACI deployment config
    deployment_config = AciWebservice.deploy_configuration(
        cpu_cores=CPU_CORES,
        memory_gb=MEMORY_GB,
    )

    print(datetime.now(), "Created deployment config.")

    # Deploy
    service = Model.deploy(
        workspace=workspace,
        name=service_name,
        models=[],
        inference_config=inference_config,
        deployment_config=deployment_config,
    )

    print(datetime.now(), "Started deployment.")

    # Wait for deployment
    service.wait_for_deployment(show_output=True)

    print(datetime.now(), "Deployment finished.")

    # Set URL in key vault
    key_vault.set_secret(name=f"{service_name}-URL", value=service.scoring_uri)

    print(datetime.now(), "URL set in key vault.")
