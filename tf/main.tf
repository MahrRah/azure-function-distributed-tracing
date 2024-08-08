
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
  monitored_queues = [
    {
      storage_account_url = "https://staammsspike.queue.core.windows.net"
      queue_name          = "testqueque"
    },
    {
      storage_account_url = "https://staammsspike.queue.core.windows.net"
      queue_name          = "testqueque"
    }
  ]
}


resource "azurerm_resource_group" "pydantictest_group" {
  name     = "tf-pydantic-test"
  location = "Switzerland North"
}

resource "azurerm_storage_account" "pydantictest_storage" {
  name                     = "pydanticteststorage"
  resource_group_name      = azurerm_resource_group.pydantictest_group.name
  location                 = azurerm_resource_group.pydantictest_group.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_app_service_plan" "pydantictest_plan" {
  name                = "ASP-pydantictestgroup-8a69"
  location            = azurerm_resource_group.pydantictest_group.location
  resource_group_name = azurerm_resource_group.pydantictest_group.name
  kind                = "Linux"
  reserved            = true

  sku {
    tier = "PremiumV3"
    size = "P1v3"
  }
}
resource "azurerm_function_app" "example" {
  name                       = "amms-spike-functions"
  location                   = azurerm_resource_group.pydantictest_group.location
  resource_group_name        = azurerm_resource_group.pydantictest_group.name
  app_service_plan_id        = azurerm_app_service_plan.pydantictest_plan.id
  storage_account_name       = azurerm_storage_account.pydantictest_storage.name
  storage_account_access_key = azurerm_storage_account.pydantictest_storage.primary_access_key
  os_type                    = "linux"
  version                    = "~4"

  app_settings = {
    "MONITORED_QUEUES" : jsonencode(local.monitored_queues)
  }
site_config {
    linux_fx_version     = "DOCKER|pydanticacr.azurecr.io/sample/func:v6"
    always_on            = true
    http2_enabled        = true
  }

}
# resource "azurerm_app_service" "pydantictest" {
#   name                = "pydanticfuncamms"
#   location            = azurerm_resource_group.pydantictest_group.location
#   resource_group_name = azurerm_resource_group.pydantictest_group.name
#   app_service_plan_id = azurerm_app_service_plan.pydantictest_plan.id

#   app_settings = {
#     "MONITORED_QUEUES" : jsonencode(local.monitored_queues)
#     "FUNCTIONS_WORKER_RUNTIME"  = "dotnet"
#     "WEBSITES_ENABLE_APP_SERVICE_STORAGE" = "false"
#   }

#   site_config {
#     always_on        = true
#     http2_enabled    = false
#   }
# }
