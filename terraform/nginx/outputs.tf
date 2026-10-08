output "app_urls" {
  description = "URLs der beiden lokalen nginx-Instanzen."
  value = {
    for name, container in docker_container.web :
    name => "http://localhost:${one(container.ports).external}"
  }
}
