pipeline {
  agent {
    docker {
      image 'astral/uv:alpine'
    }
  }

  environment {
    UV_CACHE_DIR = "${WORKSPACE}/.uv_cache"
    UV_PYTHON_INSTALL_DIR="${WORKSPACE}/.uv_python"
  }

  stages {
    stage('Build environment') {
      steps {
        sh 'uv sync --frozen'
      }
    }

    stage('Test ETL') {
      steps {
        sh 'uv run pytest'
      }
    }
  }
}
