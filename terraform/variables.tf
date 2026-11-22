variable "network_name" {
  description = "Docker network name for Library App"
  type        = string
  default     = "library-tf-network"
}

variable "app_port" {
  description = "External port for Library App"
  type        = number
  default     = 5006
}
