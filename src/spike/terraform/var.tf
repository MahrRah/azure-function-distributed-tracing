variable "resource_group_name" {
    description = "Name of the resource group"
    type        = string
    default     = "amms-spike"
}

variable "application_insights_name" {
    description = "Name of the Application Insights resource"
    type        = string
    default     = "amms-ai"
}

variable "location" {
    description = "Location of the resources"
    type        = string
    default     = "Switzerland North"
}

