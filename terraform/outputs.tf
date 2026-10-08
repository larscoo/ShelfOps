output "container_id" {
  value = docker_container.shelfops.id
}

output "container_name" {
  value = docker_container.shelfops.name
}

output "app_url" {
  value = "http://localhost:${var.host_port}"
}
