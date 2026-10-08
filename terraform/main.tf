terraform {
  required_version = ">= 1.5.0"

  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

resource "docker_image" "shelfops" {
  name         = "shelfops:${var.image_tag}"
  keep_locally = true
}

resource "docker_container" "shelfops" {
  name  = var.container_name
  image = docker_image.shelfops.image_id

  networks_advanced {
    name = docker_network.shelfops.name
  }

  volumes {
    volume_name    = docker_volume.shelfops_data.name
    container_path = "/data"
  }

  restart = "unless-stopped"

  ports {
    internal = 8000
    external = var.host_port
  }

  env = ["APP_VERSION=${var.app_version}"]
}

resource "docker_network" "shelfops" {
  name = "${var.container_name}-net"
}

resource "docker_volume" "shelfops_data" {
  name = "${var.container_name}-data"
}
