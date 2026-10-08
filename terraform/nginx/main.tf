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

resource "docker_image" "nginx" {
  name         = "nginx:alpine"
  keep_locally = true
}

resource "docker_container" "web" {
  for_each = {
    eins = var.host_port
    zwei = var.second_host_port
  }

  name  = "shelfops-week07-nginx-${each.key}"
  image = docker_image.nginx.image_id

  ports {
    internal = 80
    external = each.value
    ip       = "127.0.0.1"
  }

  volumes {
    host_path      = "${abspath(path.module)}/index.html"
    container_path = "/usr/share/nginx/html/index.html"
    read_only      = true
  }

  lifecycle {
    precondition {
      condition     = var.host_port != var.second_host_port
      error_message = "Die beiden nginx-Instanzen müssen unterschiedliche Host-Ports verwenden."
    }
  }
}
