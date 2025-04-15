pipeline {
    agent any

    environment {
        RPI_HOST = "131.152.55.25"
    }

    stages {
        stage('Connect via SSH') {
            steps {
                script {
                    sshagent(['rpi2_ssh_credentials']) {
                        sh """
                        ssh -o StrictHostKeyChecking=no ${RPI_HOST} '
                            set -e # Stop if anything goes wrong
                            echo Connection Successful!
                            ll ~/DHT22/DHT22
                            exit
                            '
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