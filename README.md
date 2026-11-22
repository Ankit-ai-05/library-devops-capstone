# End-to-End DevOps Pipeline: Library Management System (ENSP461)

A cloud-native Library Management System built with Python Flask and PostgreSQL, automated with an end-to-end DevOps pipeline covering CI/CD, Containerization, Kubernetes, Ansible, Terraform, Monitoring, Logging, Security, Blue-Green Deployment, and GitOps.

## Architecture Diagram

    Developer
       |
       v
    GitHub (main / feature branches)
       |
       v
    Jenkins CI/CD (Build -> Pytest -> SonarQube -> Docker)
       |
       v
    Docker & Kubernetes (Deployment, Service, ConfigMap, Secret, PV/PVC)
       |
       +--> Ansible & Terraform (Configuration & IaC)
       +--> Prometheus & Grafana (Monitoring)
       +--> Fluentd (Centralized Logging)
       +--> ArgoCD & Blue-Green (GitOps & Zero-Downtime Delivery)
       |
       v
    End User (http://localhost:5005)

## Project Structure
- app.py, templates/, tests/ : Flask Web App, REST APIs, Bootstrap UI, and Pytest suite
- Dockerfile, docker-compose.yml : Containerized Flask + PostgreSQL stack
- Jenkinsfile, sonar-project.properties : Automated CI/CD pipeline & SonarQube config
- k8s/ : Kubernetes Deployment, Service, ConfigMap, Secret, PV & PVC manifests
- ansible/ : Playbooks for Docker/K8s setup and app deployment
- terraform/ : Modular IaC with variables, outputs, and network module
- monitoring/ & logging/ : Prometheus, Grafana, and Fluentd configurations
- deployment/ & gitops/ : Blue-Green Nginx routing and ArgoCD GitOps manifest
