clearWorkspaceAsRoot()

@Library('jenkins_library') _

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
                    // Set image repository and name
                    env.IMAGE_REPO = "us-docker.pkg.dev/verdant-bulwark-278/vs-mcp"
                    env.IMAGE_NAME = "vs-mcp"
                    
                    def sanitisedBranch = env.BRANCH_NAME.replaceAll("/", "-").replaceAll("[^a-zA-Z0-9\\-_]+", "")
                    env.IMAGE_TAG = "${sanitisedBranch}-${env.BUILD_NUMBER}"
                    
                    // Authenticate with GCR/Artifact Registry
                    dockerLoginGCR('GoogleCredForJenkins2')
                    sh "gcloud auth configure-docker us-docker.pkg.dev --quiet"
                    
                    // Generate tags
                    def tags = [
                        "${env.IMAGE_REPO}/${env.IMAGE_NAME}:${env.IMAGE_TAG}",
                        "${env.IMAGE_REPO}/${env.IMAGE_NAME}:latest-${sanitisedBranch}"
                    ]
                    if (env.BRANCH_NAME == 'master') {
                        tags.add("${env.IMAGE_REPO}/${env.IMAGE_NAME}:latest-master")
                    } else if (env.BRANCH_NAME.contains('release')) {
                        tags.add("${env.IMAGE_REPO}/${env.IMAGE_NAME}:latest-release")
                    }
                    
                    // Build Docker image using standard Docker
                    def tagArgs = tags.collect { "-t ${it}" }.join(' ')
                    sh """
                        docker build ${tagArgs} \
                            --build-arg BUILD_NUMBER=${env.BUILD_NUMBER} \
                            --build-arg BRANCH_NAME=${env.BRANCH_NAME} \
                            --build-arg BUILD_TIME=${currentBuild.startTimeInMillis} \
                            --build-arg COMMIT_HASH=${env.GIT_COMMIT} \
                            -f Dockerfile .
                    """
                    
                    // Push all tags
                    tags.each { tag ->
                        sh "docker push ${tag}"
                    }
                    
                    // Store image details for scans
                    env.DOCKER_IMAGE = "${env.IMAGE_REPO}/${env.IMAGE_NAME}:${env.IMAGE_TAG}"
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
                    prismaCloudScanImage(
                        dockerAddress: 'unix:///var/run/docker.sock',
                        image: "${env.DOCKER_IMAGE}",
                        logLevel: 'info',
                        resultsFile: 'prisma-cloud-scan-results.json',
                        ignoreImageBuildTime: true
                    )
                    prismaCloudPublish(resultsFilePattern: 'prisma-cloud-scan-results.json')
                }
            }
        }
    }
    
    post {
        always {
            script {
                // Clean up Docker images
                sh """
                    docker rmi ${env.DOCKER_IMAGE} || true
                    docker system prune -f || true
                """
            }
            cleanWs()
        }
        success {
            script {
                echo "Build succeeded"
                // Send Slack notification on success
                slackSend(channel: "@" + getBuildUserSlackIdMB(), message: "SUCCESS <${BUILD_URL} | *${JOB_NAME}*>.", color: "#00ff00")
                slackSend(channel: "#bm-notifications-jenkins", message: "SUCCESS <${BUILD_URL} | *${JOB_NAME}*>.", color: "#00ff00")
            }
        }
        failure {
            script {
                // Send Slack notification if the pipeline fails
                def errorMessage = currentBuild.description ?: "Unknown error"
                slackSend(channel: "@" + getBuildUserSlackIdMB(), message: "FAILED <${BUILD_URL} | *${JOB_NAME}*>. Error: ${errorMessage}", color: "#ff0000")
                slackSend(channel: "#bm-alerts-blazemeter", message: "FAILED <${BUILD_URL} | *${JOB_NAME}*>. Error: ${errorMessage}", color: "#ff0000")
                
                // Send email notification
                notifyJobFailureEmailToAuthor(sender: 'jenkins@blazemeter.com')
            }
        }
    }
}
