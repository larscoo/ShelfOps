variable "container_name" {
  type    = string
  default = "shelfops"
}

variable "image_tag" {
  type    = string
  default = "local"
}

variable "app_version" {
  type    = string
  default = "1.0.0-iac"
}

variable "host_port" {
  type    = number
  default = 8001

  validation {
    condition     = var.host_port > 1024 && var.host_port <= 65535
    error_message = "host_port muss zwischen 1025 und 65535 liegen."
  }
}

