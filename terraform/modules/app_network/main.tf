variable "name" {
  type = string
}

resource "docker_network" "private_net" {
  name = var.name
}

output "network_id" {
  value = docker_network.private_net.id
}
