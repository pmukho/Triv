pipeline {
  agent any

  stages {
    stage('Build') {
      steps {
        sh 'docker-compose build'
      }
    }

    stage('Test') {
      steps {
        sh 'docker-compose run --rm backend pytest'
      }
    }

    // stage('E2E') {
    //   steps {
    //     sh './scripts/spawn_mock_frontends.sh'
    //   }
    // }

    stage('Deploy') {
      when {
        branch 'main'
      }
      steps {
        sh './scripts/deploy.sh'
      }
    }
  }
}
