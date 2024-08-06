
#----------------------------------------------------------------
# Create alert rules 
#----------------------------------------------------------------

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0" # Use an appropriate version
    }
    azapi = {
      source  = "azure/azapi"
      version = "~> 1.0" # Adjust to the latest appropriate version
    }
  }
}

provider "azurerm" {
  features {}
}

locals {
  env = "dev"
  queue_name_one = "orchestrator-azureml-events-length"
  queue_name_two = "service-ml-backend-events-length"
}

resource "azurerm_resource_group" "rg" {
  name     = "azure-functions-test-rg"
  location = "West Europe"
}


resource "azurerm_storage_account" "example" {
  name                     = "blublablabublabla"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_app_service_plan" "example" {
  name                = "azure-functions-test-service-plan"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  sku {
    tier = "Standard"
    size = "S1"
  }
}

locals {
  monitored_queues = [
    {
      storage_account_url = "https://staammsspike.queue.core.windows.net"
      queue_name          =  "testqueque"
    },
    {
      storage_account_url = "https://staammsspike.queue.core.windows.net"
      queue_name          = "testqueque"
    }
  ]
}

resource "azurerm_function_app" "example" {
  name                       = "amms-spike-functions"
  location                   = azurerm_resource_group.rg.location
  resource_group_name        = azurerm_resource_group.rg.name
  app_service_plan_id        = azurerm_app_service_plan.example.id
  storage_account_name       = azurerm_storage_account.example.name
  storage_account_access_key = azurerm_storage_account.example.primary_access_key
  app_settings = {
    "MONITORED_QUEUES": jsonencode(local.monitored_queues)
  }
}
