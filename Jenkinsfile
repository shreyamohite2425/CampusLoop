pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '"C:\\Users\\Shreya\\AppData\\Local\\Python\\pythoncore-3.15-64\\python.exe" -m pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                bat '"C:\\Users\\Shreya\\AppData\\Local\\Python\\pythoncore-3.15-64\\python.exe" -m pytest -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t campusloop .'
            }
        }

        stage('Deploy') {
            steps {
                bat 'docker rm -f campusloop-app || exit /b 0'
                bat 'docker run -d --name campusloop-app -p 5000:5000 campusloop'
            }
        }
    }
}