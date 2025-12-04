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
                    // Authenticate with GCP Artifact Registry in jenkins-docker-agent container
                    container('jenkins-docker-agent') {
                        withCredentials([file(credentialsId: 'GoogleCredForJenkins2', variable: 'GCP_KEY')]) {
                            sh """
                                cat \${GCP_KEY} | docker login -u _json_key --password-stdin https://us-docker.pkg.dev
                            """
                        }
                    }
                    
                    BuildkitManager buildkit = new BuildkitManager(this)
                    def sanitisedBranch = env.BRANCH_NAME.replaceAll("/", "-").replaceAll("[^a-zA-Z0-9\\-_]+", "")
                    def tags = [
                        "us-docker.pkg.dev/verdant-bulwark-278/vs-mcp/vs-mcp:${sanitisedBranch}-${env.BUILD_NUMBER}",
                        "us-docker.pkg.dev/verdant-bulwark-278/vs-mcp/vs-mcp:latest-${sanitisedBranch}"
                    ]
                    if (env.BRANCH_NAME == 'master') {
                        tags.add("us-docker.pkg.dev/verdant-bulwark-278/vs-mcp/vs-mcp:latest-master")
                    } else if (env.BRANCH_NAME.contains('release')) {
                        tags.add("us-docker.pkg.dev/verdant-bulwark-278/vs-mcp/vs-mcp:latest-release")
                    }
                    
                    buildkit.build(tags: tags)
                    
                    // Store buildkit and image details for scans
                    this.buildkit = buildkit
                    env.IMAGE_REPO = "us-docker.pkg.dev/verdant-bulwark-278/vs-mcp"
                    env.IMAGE_NAME = "vs-mcp"
                    env.IMAGE_TAG = "${sanitisedBranch}-${env.BUILD_NUMBER}"
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
                    buildkit.pull("${env.IMAGE_REPO}/${env.IMAGE_NAME}:${env.IMAGE_TAG}")
                    prismaCloudScanImage(
                        dockerAddress: 'unix:///var/run/docker.sock',
                        image: "${env.IMAGE_REPO}/${env.IMAGE_NAME}:${env.IMAGE_TAG}",
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
                if (binding.hasVariable('buildkit') && buildkit != null) {
                    buildkit.cleanImages()
                }
            }
            cleanWs()
        }
        success {
            script {
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
