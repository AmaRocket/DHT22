pipeline {
    agent any

    environment {
        RPI_HOST = credentials("rpi_ip")
        USER = credentials("ssh_user")
    }

    stages {
        stage('Clone Repository') {
            steps {
                dir('/var/lib/jenkins/workspace/RPI2_Temperature_Measurement/') {
                    script {
                        if (fileExists('.git') && sh(script: 'git rev-parse --is-inside-work-tree', returnStatus: true) == 0) {
                            sh 'git reset --hard'
                            sh 'git clean -fdx'
                            sh 'rm -f .git/config.lock || true'
                            sh 'git pull origin main'
                        } else {
                            deleteDir()
                            git branch: 'main', url: 'https://github.com/AmaRocket/DHT22.git'
                        }
                    }
                }
            }
        }

        stage('Connect via SSH') {
            steps {
                script {
                    sshagent(['rpi2_ssh_credentials']) {
                        sh """
                        ssh -o StrictHostKeyChecking=no \$USER@\${RPI_HOST} '
                            set -e # Stop if anything goes wrong
                            echo Connection Successful!
                            cd /home/localadmin/DHT22/DHT22
                            git stash
                            echo "Pulling latest code..."
                            git pull

                            # Check if the systemd service is running and restart it if necessary
                            echo "Installing dependencies"
                            source ../../dht_env/bin/activate
                            pip install -r requirements.txt

                            echo "Restarting DHT22 app via systemd..."
                            sudo systemctl reload-or-restart temp-app.service

                            echo "Deployment finished!"
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
