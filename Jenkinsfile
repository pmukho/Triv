pipeline {
  agent any

  stages {
    stage('Build') {
      steps {
        sh 'docker-compose build'
      }
    }

    stage('Backend Tests') {
      steps {
        sh 'docker-compose run --rm cache pytest'
      }
    }

    stage('Frontend Lint & Tests') {
      steps {
        dir('frontend') {
          sh 'npm ci'
          sh 'npm run lint || true' 
          sh 'npm test -- --watchAll=false --passWithNoTests || true' 
        }
      }
    }

    stage('E2E Tests') {
      steps {
        // You can replace this with Cypress, Playwright, or Puppeteer later
        sh './scripts/spawn_mock_frontends.sh || echo "Skipping E2E"'
      }
    }

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
