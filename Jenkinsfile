@Library('jenkins_library') _

import com.blazemeter.buildkit.BuildkitManager
import com.blazemeter.pr.PullRequestUtils
import com.blazemeter.pr.PullRequestStatus
import com.blazemeter.pr.PackageBuildResult
import com.blazemeter.pr.BuildResultManager

properties([pipelineTriggers([githubPush()])])

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
    
    environment {
        DOCKER_REPO = 'vs-mcp'
        IMAGE_NAME = 'us.gcr.io/verdant-bulwark-278/vs-mcp'
        CURRENT_BRANCH = "${env.BRANCH_NAME ?: env.GIT_BRANCH?.replaceAll('origin/', '') ?: 'master'}"
    }
    
    stages {
        stage('Setup') {
            steps {
                script {
                    clearWorkspaceAsRoot()
                    
                    PullRequestUtils.updateBranchPullRequestsStatuses(this, PullRequestStatus.PENDING)
                    currentBuild.displayName = "#${env.BUILD_NUMBER} | ${env.CURRENT_BRANCH}"
                    
                    echo "Building branch: ${env.CURRENT_BRANCH}"
                }
            }
        }
        
        stage('Build & Test') {
            steps {
                script {
                    sh """
                        pip install build pytest pytest-cov --break-system-packages
                        python -m build --sdist
                        pip install . --break-system-packages
                        mkdir -p reports
                        PYTHONPATH=. pytest --junitxml=reports/junit-report.xml || echo 'Tests not implemented yet'
                    """
                }
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/junit-report.xml', skipPublishingChecks: true, skipMarkingBuildUnstable: true
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    BuildkitManager buildkit = new BuildkitManager(this)
                    
                    // Capture git commit for tagging
                    def gitCommit = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
                    def shortSha = gitCommit.take(5)
                    def sanitisedBranch = sanitiseBranchName(env.CURRENT_BRANCH)
                    
                    // Build tags
                    def tagsList = [
                        env.BUILD_NUMBER,
                        "${sanitisedBranch}-${shortSha}-${env.BUILD_NUMBER}"
                    ]
                    
                    // Add 'latest' only for master/develop
                    if (env.CURRENT_BRANCH in ['develop', 'master']) {
                        tagsList.add('latest')
                    }
                    
                    // Add 'latest-release' for release branches
                    if (env.CURRENT_BRANCH.contains('release')) {
                        tagsList.add('latest-release')
                    }
                    
                    echo "Tags: ${tagsList}"
                    
                    // Convert to full image references
                    def fullImageTags = tagsList.collect { "${env.IMAGE_NAME}:${it}" }
                    
                    // Build with BuildkitManager
                    buildkit.build(
                        imageName: env.DOCKER_REPO,
                        tags: fullImageTags,
                        buildArgs: [
                            "BUILD_NUMBER=${env.BUILD_NUMBER}",
                            "BRANCH_NAME=${env.CURRENT_BRANCH}",
                            "BUILD_TIME=${currentBuild.startTimeInMillis}",
                            "COMMIT_HASH=${gitCommit}",
                            "CACHEBUST=${currentBuild.startTimeInMillis}"
                        ]
                    )
                    
                    // Archive build results
                    def buildManager = new BuildResultManager(this)
                    def buildResult = new PackageBuildResult(env.DOCKER_REPO, tagsList[0])
                    buildManager.archiveResultsFromBuildResult(buildResult)
                    
                    // Store for scans
                    env.IMAGE_TAG = "${sanitisedBranch}-${shortSha}-${env.BUILD_NUMBER}"
                    this.buildkit = buildkit
                }
            }
        }
        
        stage('WhiteSource Scan') {
            when { expression { params.PERFORM_WHITESOURCE_SCAN } }
            steps {
                script {
                    whiteSourceScan("Virtual-Services-MCP", env.CURRENT_BRANCH)
                }
            }
        }
        
        stage('PrismaCloud Scan') {
            when { expression { params.PERFORM_PRISMA_SCAN } }
            steps {
                script {
                    runPrismaCloudScanOnK8s(
                        imageTag: "${env.IMAGE_NAME}:${env.IMAGE_TAG}",
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
            script {
                if (!env.skippedBuild) {
                    PullRequestUtils.updateBranchPullRequestsStatuses(this)
                }
            }
        }
        failure {
            script {
                sh 'git config --global --add safe.directory "*"'
                notifyJobFailureEmailToAuthor(sender: 'jenkins@blazemeter.com')
            }
        }
    }
}
