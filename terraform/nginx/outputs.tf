output "app_url" {
  description = "URL der lokalen nginx-Übungsseite."
  value       = "http://localhost:${var.host_port}"
}
