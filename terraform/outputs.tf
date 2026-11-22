output "network_id" {
  description = "Created Docker Network ID"
  value       = module.app_network.network_id
}

output "app_url" {
  description = "Provisioned Application URL"
  value       = "http://localhost:${var.app_port}"
}
