pipeline {
    agent any

    environment {
        RPI_USER = "localadmin"
        RPI_HOST = "131.152.55.25"
    }

    stages {
        stage('Connect via SSH') {
            steps {
                script {
                    sshagent(['rpi2_ssh_credentials']) {
                        sh """
                        ssh -o StrictHostKeyChecking=no ${RPI_USER}@${RPI_HOST} "set -e; neofetch"
                        """
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