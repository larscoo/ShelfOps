variable "host_port" {
  description = "Lokaler Port für die nginx-Übungsseite."
  type        = number
  default     = 8082

  validation {
    condition     = var.host_port > 1024 && var.host_port <= 65535 && floor(var.host_port) == var.host_port
    error_message = "host_port muss eine ganze Zahl zwischen 1025 und 65535 sein."
  }
}

variable "second_host_port" {
  description = "Lokaler Port für die zweite nginx-Instanz."
  type        = number
  default     = 8083

  validation {
    condition     = var.second_host_port > 1024 && var.second_host_port <= 65535 && floor(var.second_host_port) == var.second_host_port
    error_message = "second_host_port muss eine ganze Zahl zwischen 1025 und 65535 sein."
  }
}
