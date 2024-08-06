
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

# data "azurerm_logic_app_workflow" "teams_notification" {
#   name                = "alert-app-amms"
#   resource_group_name = "amms-spike"
# }

data "azurerm_application_insights" "app_insighst" {
  name                = var.application_insights_name
  resource_group_name = var.resource_group_name
}

# data "azapi_resource_action" "logicapp_callbackurl" {
#   resource_id            = "${data.azurerm_logic_app_workflow.teams_notification.id}/triggers/manual"
#   action                 = "listCallbackUrl"
#   type                   = "Microsoft.Logic/workflows/triggers@2018-07-01-preview"
#   response_export_values = ["value"]
# }
# resource "azurerm_monitor_action_group" "teams_action_group" {
#   name                = "TeamsNotificationAction"
#   resource_group_name = var.resource_group_name
#   short_name          = "TeamsNotif"

#   logic_app_receiver {
#     name                    = data.azurerm_logic_app_workflow.teams_notification.name
#     resource_id             = data.azurerm_logic_app_workflow.teams_notification.id
#     callback_url            = jsondecode(data.azapi_resource_action.logicapp_callbackurl.output).value
#     use_common_alert_schema = true
#   }

#   lifecycle {
#     ignore_changes = [
#       tags
#     ]
#   }
# }

resource "azurerm_monitor_metric_alert" "error_logs_alert" {
  name                     = "Warning, Error and Critical Log Alert - ${title(local.env)}"
  resource_group_name      = var.resource_group_name
  scopes                   = [data.azurerm_application_insights.app_insighst.id]
  description              = "Alerting on 1 or more log line of level Warning, Error or Critical."
  target_resource_location = var.location

  criteria {
    metric_name            = "traces/count"
    metric_namespace       = "microsoft.insights/components"
    aggregation            = "Count"
    operator               = "GreaterThan"
    skip_metric_validation = false
    threshold              = 1
    dimension {
      name     = "trace/severityLevel"
      operator = "Include"
      values   = ["3", "4", "5"]
    }
    dimension {
      name     = "cloud/roleName"
      operator = "Include"
      values   = ["*"]
    }

  }
  auto_mitigate = false
  severity      = 1
  frequency     = "PT1M"
  window_size   = "PT5M"

  # action {
  #   action_group_id = azurerm_monitor_action_group.teams_action_group.id
  # }

  lifecycle {
    ignore_changes = [
      tags["SEALZ-CostCenter"],
      tags["SEALZ-BusinessUnit"],
      tags["SEALZ-DataClassification"],
    ]
  }
}

resource "azurerm_monitor_scheduled_query_rules_alert_v2" "example" {
  name                = "Poisen queue alert"
  resource_group_name = var.resource_group_name
  scopes              = [data.azurerm_application_insights.app_insighst.id]
  description         = "Alerting if there is a message in a poisen queue."
  location            = var.location
 
  evaluation_frequency = "PT10M"
  window_duration      = "PT10M"
  severity             = 4
  criteria {
    query                   = <<-QUERY
      customMetrics
        | where name in ("${local.queue_name_one}", "${local.queue_name_two}")
        | summarize avg(value) by name, bin(timestamp, 10m)
 
      QUERY
    time_aggregation_method = "Average"
    threshold               = 1
    operator                = "GreaterThan"
    metric_measure_column =  "avg_value"
    dimension {
      name     = "name"
      operator = "Include"
      values   = ["*"]
    }
    failing_periods {
      minimum_failing_periods_to_trigger_alert = 1
      number_of_evaluation_periods             = 1
    }
  }
 
  auto_mitigation_enabled          = true
  enabled                          = true
  query_time_range_override        = "PT1H"
  skip_query_validation            = true
 
  lifecycle {
    ignore_changes = [
      tags["SEALZ-CostCenter"],
      tags["SEALZ-BusinessUnit"],
      tags["SEALZ-DataClassification"],
    ]
  }
}

resource "azurerm_monitor_metric_alert" "missing_service_logs_alert" {
  name                     = "Missing log lines Alert"
  resource_group_name      = var.resource_group_name
  scopes                   = [data.azurerm_application_insights.app_insighst.id]
  target_resource_location = var.location
  description              = "Alerting if services do not send anymore logs."

  criteria {
    metric_namespace = "microsoft.insights/components"
    metric_name      = "traces/count"
    aggregation      = "Count"
    operator         = "LessThanOrEqual"
    threshold        = 0

    dimension {
      name     = "cloud/roleName"
      operator = "Include"
      values   = ["*"]
    }
  }
  # action {
  #   action_group_id = azurerm_monitor_action_group.teams_action_group.id
  # }
  lifecycle {
    ignore_changes = [
      tags["SEALZ-CostCenter"],
      tags["SEALZ-BusinessUnit"],
      tags["SEALZ-DataClassification"]
    ]
  }
}

resource "azurerm_monitor_metric_alert" "exception_alert" {
  name                     = "Uncaught Exception Alert"
  resource_group_name      = var.resource_group_name
  scopes                   = [data.azurerm_application_insights.app_insighst.id]
  description              = "Alerting if services throws uncaught exception."
  target_resource_location = var.location

  criteria {
    metric_name            = "exceptions/count"
    metric_namespace       = "microsoft.insights/components"
    aggregation            = "Count"
    operator               = "GreaterThan"
    skip_metric_validation = false
    threshold              = 1

    dimension {
      name     = "cloud/roleName"
      operator = "Include"
      values   = ["*"]
    }
  }

  auto_mitigate = true
  severity      = 1
  frequency     = "PT1M"
  window_size   = "PT30M"

  # action {
  #   action_group_id = azurerm_monitor_action_group.teams_action_group.id
  # }

  lifecycle {
    ignore_changes = [
      tags["SEALZ-CostCenter"],
      tags["SEALZ-BusinessUnit"],
      tags["SEALZ-DataClassification"],
    ]
  }
}




