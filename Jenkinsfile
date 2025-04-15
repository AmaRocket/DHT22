pipeline {
    agent any

    environment {
        RPI_HOST = credentials("rpi_ip")
        USER = credentials("admin_username")
        APP_PATH = credentials("rpi_app_path")
    }

    stages {
        stage('Clone Repository') {
            steps {
                dir('/var/lib/jenkins/workspace/RPI2_Temperature_Measurement/') {
                    script {
                        if (fileExists('.git')) {
                            sh 'git stash || true'
                            sh 'git pull origin main'
                        } else {
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
                            cd \$APP_PATH
                            echo "Pulling latest code..."
                            sudo git pull

                            echo "Checking if port 5000 is in use..."
                            PID=\$(sudo lsof -ti:5000)

                            if [ ! -z "\$PID" ]; then
                                echo "Killing process \$PID using port 5000"
                                sudo kill -9 \$PID
                                sleep 2
                            fi

                            echo "Starting Flask app..."
                            nohup python3 app.py > flask.log 2>&1 &

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
