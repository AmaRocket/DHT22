pipeline {
    agent any

    environment {
        RPI_HOST = "131.152.55.25"
        MAAS_USER = "localadmin"
        SSH_KEY = credentials('rpi_ssh_key')
    }

    stages {
        stage('Connect via SSH') {
            steps {
                script {
                    sshagent(['rpi2_ssh_credentials']) {
                        sh """
                        ssh -o StrictHostKeyChecking=no \$MAAS_USER@\${REGION_CONTROLLER_IP} '
                            set -e # Stop if anything goes wrong
                            echo Connection Successful!
                            '
                        """
                        echo "Checking if port 5000 is free..."
                            sh '''
                            PORT=5000
                            if netstat -tuln | grep -q ":$PORT "; then
                                echo "Port $PORT is already in use. Stopping process..."
                                fuser -k $PORT/tcp || true
                            fi
                            '''
                    }
                }
            }
        }
    }

    post {
        success {
            echo '✅ Deployment successful!'
        }
        failure {
            echo '❌ Deployment failed.'
        }
    }
}