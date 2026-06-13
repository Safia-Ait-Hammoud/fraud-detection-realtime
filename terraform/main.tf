# 1. Configuration du fournisseur Cloud (AWS)
provider "aws" {
  region = "eu-west-3" # Région Paris (la plus proche du Maroc pour une bonne latence)
}

# 2. Recherche automatique de la dernière image Ubuntu 22.04 gratuite
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # ID officiel de Canonical (Ubuntu)

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

# 3. Création du Pare-feu (Security Group)
resource "aws_security_group" "fraud_sg" {
  name        = "fraud_project_sg"
  description = "Autoriser SSH, API et Grafana"

  # Accès SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] 
  }

  # Accès à API FastAPI
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Accès à Grafana
  ingress {
    from_port   = 3000
    to_port     = 3002
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Autoriser la machine à télécharger des paquets sur internet
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 4. Création de la Machine Virtuelle (Instance EC2)
resource "aws_instance" "fraud_server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "m7i-flex.large"
  
  vpc_security_group_ids = [aws_security_group.fraud_sg.id]
  
  key_name = "fraud-project-key" 

  # Disque dur de 30 Go
  root_block_device {
    volume_size = 30
    volume_type = "gp3"
  }

  # 5. Le script de post-démarrage
  user_data = <<-EOF
              #!/bin/bash
              # Création du SWAP de 6 Go pour supporter Kafka et Spark
              fallocate -l 6G /swapfile
              chmod 600 /swapfile
              mkswap /swapfile
              swapon /swapfile
              echo '/swapfile none swap sw 0 0' | tee -a /etc/fstab

              # Installation de Docker et Docker Compose
              apt-get update
              apt-get install -y apt-transport-https ca-certificates curl software-properties-common git
              curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
              add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
              apt-get update
              apt-get install -y docker-ce docker-compose-plugin
              usermod -aG docker ubuntu
              EOF

  tags = {
    Name = "FraudDetection-Server"
  }
}

# Afficher l'adresse IP publique à la fin
output "public_ip" {
  value       = aws_instance.fraud_server.public_ip
  description = "L'adresse IP pour te connecter à ta machine"
}