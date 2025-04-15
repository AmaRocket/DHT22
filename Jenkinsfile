pipeline {
    agent any

    environment {
        RPI_HOST = credentials("rpi_ip")
        USER = credentials("admin_username")
    }

    stages {
        stage('Connect via SSH') {
            steps {
                script {
                    sshagent(['rpi2_ssh_credentials']) {
                        sh """
                        ssh -o StrictHostKeyChecking=no \$USER@\${RPI_HOST} '
                            set -e # Stop if anything goes wrong
                            echo Connection Successful!
                            '
                        """
                        sh '''
                            exit
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