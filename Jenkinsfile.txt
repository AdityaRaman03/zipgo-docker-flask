pipeline {
    agent any

    environment {
        IMAGE_NAME     = "zipgo-svc"
        IMAGE_TAG      = "1"
        CONTAINER_NAME = "zipgo-svc-container"
        APP_PORT       = "12096"
    }

    stages {
        stage('Pre-check Docker') {
            steps {
                script {
                    echo "Checking if Docker is available..."
                    // Returns 0 if ok, non-zero if docker is missing/broken
                    def status = sh(script: "docker --version", returnStatus: true)
                    if (status != 0) {
                        error "Docker is not installed or not available in PATH. Failing pipeline."
                    }
                }
            }
        }

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker image ${IMAGE_NAME}:${IMAGE_TAG}..."
                sh """
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                """
            }
        }

        stage('Run Container') {
            steps {
                script {
                    echo "Stopping any existing container with name ${CONTAINER_NAME}..."
                    sh """
                        if [ \$(docker ps -aq -f name=${CONTAINER_NAME}) ]; then
                            docker stop ${CONTAINER_NAME} || true
                            docker rm ${CONTAINER_NAME} || true
                        fi
                    """

                    echo "Starting new container on port ${APP_PORT}..."
                    sh """
                        docker run -d \
                            --name ${CONTAINER_NAME} \
                            -p ${APP_PORT}:${APP_PORT} \
                            ${IMAGE_NAME}:${IMAGE_TAG}

                        echo "Current running containers:"
                        docker ps
                    """
                }
            }
        }

        stage('Verify Service') {
            steps {
                script {
                    echo "Verifying service on http://localhost:${APP_PORT}/ ..."
                    sh """
                        sleep 5
                        curl -v --fail http://localhost:${APP_PORT}/ || (echo "Health check failed" && exit 1)
                    """
                }
            }
        }
    }

    post {
        success {
            echo "ZipGo Dockerized Flask service is running successfully on port ${APP_PORT}."
        }
        failure {
            echo "Pipeline failed. Check logs for details."
        }
    }
}
