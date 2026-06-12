@Library('jenkins_library') _
import com.blazemeter.buildkit.BuildkitManager

BuildkitManager buildkit = new BuildkitManager(this)

clearWorkspaceAsRoot()

pipeline {
    agent {
        kubernetes {
            yaml agentYaml(additionalContainers: ['k8s.yaml'])
            defaultContainer 'jenkins-docker-agent'
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
                // k8s agent workspace is owned by a different uid than the step user
                sh 'git config --global --add safe.directory "*"'
                sh "pip install uv --break-system-packages"
            }
        }
        
        stage('Build') {
            steps {
                sh "uv sync --frozen"
                sh "uv build --sdist"
            }
        }
        
        stage('Test') {
            steps {
                sh "uv run pytest --junitxml=reports/junit-report.xml"
                junit allowEmptyResults: true, testResults: 'reports/junit-report.xml', skipPublishingChecks: true, skipMarkingBuildUnstable: true
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    // Set image repository and name
                    env.IMAGE_REPO = "us-docker.pkg.dev/verdant-bulwark-278/sv-mcp"
                    env.IMAGE_NAME = "sv-mcp"
                    
                    def sanitisedBranch = env.BRANCH_NAME.replaceAll("/", "-").replaceAll("[^a-zA-Z0-9\\-_]+", "")
                    env.IMAGE_TAG = "${sanitisedBranch}-${env.BUILD_NUMBER}"

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

                    // Build & push on buildkit (push auth via podfleet Workload Identity)
                    buildkit.build(
                        dockerFile: 'Dockerfile',
                        buildArgs: [
                            "BUILD_NUMBER=${env.BUILD_NUMBER}",
                            "BRANCH_NAME=${env.BRANCH_NAME}",
                            "BUILD_TIME=${currentBuild.startTimeInMillis}",
                            "COMMIT_HASH=${env.GIT_COMMIT}"
                        ],
                        tags: tags
                    )

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
                    runPrismaCloudScanOnK8s(
                        imageTag: "${env.DOCKER_IMAGE}",
                        buildkitManager: buildkit
                    )
                }
            }
        }
    }
    
    post {
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
                // def errorMessage = currentBuild.description ?: "Unknown error"
                // slackSend(channel: "@" + getBuildUserSlackIdMB(), message: "FAILED <${BUILD_URL} | *${JOB_NAME}*>. Error: ${errorMessage}", color: "#ff0000")
                // slackSend(channel: "#bm-alerts-blazemeter", message: "FAILED <${BUILD_URL} | *${JOB_NAME}*>. Error: ${errorMessage}", color: "#ff0000")
                
                // Send email notification
                notifyJobFailureEmailToAuthor(sender: 'jenkins@blazemeter.com')
            }
        }
        cleanup {
            cleanWs()
        }
    }
}
