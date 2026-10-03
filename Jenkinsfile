pipeline {
    agent any

    environment {
        IMAGE_NAME = 'police-misconduct-outcomes-mvp'
    }

    stages {
        stage('Build Docker image') {
            steps {
                sh 'docker build --tag "$IMAGE_NAME:$BUILD_NUMBER" .'
            }
        }

        stage('Run demo analysis') {
            steps {
                sh '''
                    mkdir -p reports
                    docker run --rm \
                        --user "$(id -u):$(id -g)" \
                        --volume "$WORKSPACE/reports:/reports" \
                        "$IMAGE_NAME:$BUILD_NUMBER"
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/summary.json,reports/outcomes.png', allowEmptyArchive: true
        }
    }
}
