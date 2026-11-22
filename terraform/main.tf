terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

module "app_network" {
  source = "./modules/app_network"
  name   = var.network_name
}

resource "docker_container" "library_tf_app" {
  name  = "library-web-terraform"
  image = "library-devops-capstone-web:latest"
  ports {
    internal = 5005
    external = var.app_port
  }
  networks_advanced {
    name = var.network_name
  }
  depends_on = [module.app_network]
}
