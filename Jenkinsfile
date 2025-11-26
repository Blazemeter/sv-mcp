clearWorkspaceAsRoot()

@Library('jenkins_library') _

import com.blazemeter.buildkit.BuildkitManager

pipeline {
    agent {
        kubernetes {
            yaml agentYaml()
            defaultContainer 'jenkins-docker-agent'
            workspaceVolume dynamicPVC(accessModes: 'ReadWriteOnce', requestsSize: "5Gi", storageClassName: "standard-rwo")
        }
    }
    
    parameters {
        booleanParam(name: 'PERFORM_PRISMA_SCAN', defaultValue: true, description: 'Perform a Prisma scan for the Docker image')
        booleanParam(name: 'PERFORM_WHITESOURCE_SCAN', defaultValue: true, description: 'Perform a WhiteSource scan for the code')
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '100', daysToKeepStr: '45'))
        ansiColor('xterm')
        timestamps()
        disableConcurrentBuilds()
    }
    
    stages {
        stage('Setup') {
            steps {
                script {
                    currentBuild.displayName = "#${env.BUILD_NUMBER}"
                }
            }
        }
        
        stage('Build') {
            steps {
                script {
                    sh "pip install build --break-system-packages"
                    sh "python -m build --sdist"
                    sh "pip install . --break-system-packages"
                }
            }
        }
        
        stage('Test') {
            steps {
                sh "pip install . --break-system-packages"
                sh "PYTHONPATH=. pytest --junitxml=reports/junit-report.xml"
                junit allowEmptyResults: true, testResults: 'reports/junit-report.xml', skipPublishingChecks: true, skipMarkingBuildUnstable: true
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    BuildkitManager buildkit = new BuildkitManager(this)
                    buildkit.build(imageName: "vs-mcp")
                    
                    // Store buildkit for scans
                    this.buildkit = buildkit
                }
            }
        }
        
        stage('WhiteSource Scan') {
            when { expression { params.PERFORM_WHITESOURCE_SCAN } }
            steps {
                script {
                    whiteSourceScan("Virtual-Services-MCP", env.BRANCH_NAME)
                }
            }
        }
        
        stage('PrismaCloud Scan') {
            when { expression { params.PERFORM_PRISMA_SCAN } }
            steps {
                script {
                    runPrismaCloudScanOnK8s(
                        imageTag: "us.gcr.io/verdant-bulwark-278/vs-mcp:${env.BUILD_NUMBER}",
                        buildkitManager: this.buildkit
                    )
                }
            }
        }
    }
    
    post {
        always {
            smartSlackNotification(
                alternateJobTitle: 'VS-MCP package build',
                notifyOnSuccess: true
            )
        }
        failure {
            notifyJobFailureEmailToAuthor(sender: 'jenkins@blazemeter.com')
        }
    }
}
