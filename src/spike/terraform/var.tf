variable "resource_group_name" {
    description = "Name of the resource group"
    type        = string
    default     = "af-amms-demo_group"
}

variable "application_insights_name" {
    description = "Name of the Application Insights resource"
    type        = string
    default     = "af-amms-demo"
}

variable "location" {
    description = "Location of the resources"
    type        = string
    default     = "Switzerland North"
}

