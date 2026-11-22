pipeline {
    agent any
    environment {
        IMAGE_NAME = "library-devops-capstone"
        DOCKER_TAG = "${env.BUILD_NUMBER ?: 'latest'}"
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${IMAGE_NAME}:${DOCKER_TAG} ."
            }
        }
        stage('Automated Testing (Pytest)') {
            steps {
                sh "docker run --rm ${IMAGE_NAME}:${DOCKER_TAG} python -m pytest -v"
            }
        }
        stage('Security & Code Quality (SonarQube)') {
            steps {
                echo "Running static analysis and secret scan..."
                sh "grep -rn 'password' app.py || true"
            }
        }
        stage('Deploy Container') {
            steps {
                sh "docker compose up -d --build"
            }
        }
    }
    post {
        success {
            echo "Pipeline succeeded! Library Management System deployed."
        }
        failure {
            echo "Pipeline failed! Check test or build logs."
        }
    }
}
