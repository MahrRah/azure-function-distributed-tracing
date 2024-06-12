#!/bin/bash

# For project-name use only alphanumeric characters
create_resource_group() {
    echo "- Create resource group $ENV_PROJECT_NAME-rg"
    az group create \
    --location "$ENV_LOCATION" \
    --name "$ENV_PROJECT_NAME-rg"
    
    echo "- Resrouce group $ENV_PROJECT_NAME-rg created"
    echo ""
}

create_infrastructure(){
    echo "- Create all needed resources in resource group $ENV_PROJECT_NAME-rg"
    az deployment group create \
    --resource-group "$ENV_PROJECT_NAME-rg" \
    --template-file ./infra/main.bicep \
    --parameters projectName="$ENV_PROJECT_NAME"

    echo "- Resources created in resource group $ENV_PROJECT_NAME-rg"
    echo ""
}


delete_infrastructure(){
    echo "- Delete resource group $ENV_PROJECT_NAME-rg"
    az group delete \
    --name "$ENV_PROJECT_NAME-rg" \
    --yes
    echo "- Deleted resource group $ENV_PROJECT_NAME-rg"
    echo ""
}

run_main() {
    
    # .env included in root of repo
    # shellcheck disable=SC1091
    source .env
    
    if [[ "$1" == "--create" ]] || [[ "$1" == "-c" ]]; then
        echo "--- Creating infrastructure ---"
        create_resource_group
        create_infrastructure
        exit 0
        
    elif [[ "$1" == "--delete" ]] || [[ "$1" == "-d" ]]; then
        echo "--- Deleting infrastructure ---"
        delete_infrastructure
        exit 0
    else
        echo "Usage: $0 [--create | -c] | [--delete | -d]"
        exit 1
    fi
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    run_main "$@"
fi