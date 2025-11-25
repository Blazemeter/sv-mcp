@Library('jenkins_library')
import com.blazemeter.buildkit.BuildkitManager
import com.blazemeter.pr.PullRequestUtils
import com.blazemeter.pr.PullRequestStatus
import com.blazemeter.pr.PackageBuildResult
import com.blazemeter.pr.BuildResultManager

BuildkitManager buildkit = new BuildkitManager(this)

properties([pipelineTriggers([githubPush()])]) //Enable Git webhook triggering

pipeline {
    parameters {
        booleanParam(name: 'PERFORM_PRISMA_SCAN', defaultValue: true, description: 'Perform a Prisma scan for the Docker image')
        booleanParam(name: 'FAIL_JOB_ON_SCAN_FAILURES', defaultValue: false, description: 'If checked, Twistlock vulnerabilities scan will enforce job failure.')
        booleanParam(name: 'PERFORM_WHITESOURCE_SCAN', defaultValue: true, description: 'Perform a WhiteSource scan for the code')
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '100', daysToKeepStr: '45'))
        ansiColor('xterm')
        timestamps()
        disableConcurrentBuilds()
    }

    agent {
        kubernetes {
            yaml agentYaml()
            defaultContainer 'jenkins-docker-agent'
            workspaceVolume dynamicPVC(accessModes: 'ReadWriteOnce', requestsSize: "5Gi", storageClassName: "standard-rwo")
        }
    }
    
    environment {
        project = 'Virtual-Services-MCP-Server'
        DOCKER_REPO = 'vs-mcp'
        IMAGE_NAME = 'us.gcr.io/verdant-bulwark-278/vs-mcp'
        TMPDIR = '/tmp'
        SENDER = 'jenkins@blazemeter.com'
    }
    
    stages {
        stage('Setup') {
            steps {
                script {
                    // Capture branch name from the declarative checkout before clearing workspace
                    env.CURRENT_BRANCH = env.BRANCH_NAME ?: env.GIT_BRANCH?.replaceAll('origin/', '') ?: 'master'
                    // Keep BRANCH_NAME set for compatibility with BuildkitManager and other tools
                    if (!env.BRANCH_NAME) {
                        env.BRANCH_NAME = env.CURRENT_BRANCH
                    }
                    echo "Building branch: ${env.CURRENT_BRANCH}"
                    
                    PullRequestUtils.updateBranchPullRequestsStatuses(this, PullRequestStatus.PENDING)
                    env.MODIFIED_BUILD_NUMBER = env.BUILD_NUMBER
                    currentBuild.displayName = "#${MODIFIED_BUILD_NUMBER} | [Node] ${env.NODE_NAME} | ${env.CURRENT_BRANCH}"
                }
            }
        }
        
        stage('Clone') {
            steps {
                script {
                    clearWorkspace()
                    sh 'git config --global --add safe.directory "*"'
                    
                    checkoutVars = repositoryDirectoryCheckout('Virtual-Services-MCP-Server', 'Virtual-Services-MCP-Server', env.CURRENT_BRANCH)
                    dir("Virtual-Services-MCP-Server") {
                        sh 'git config --global --add safe.directory "*"'
                        commitDate = sh script: 'git log -1 --format="%ad %H"', returnStdout: true
                        sh """
                            echo -n '$JOB_NAME $BUILD_NUMBER ${env.CURRENT_BRANCH} ${checkoutVars.GIT_COMMIT} $commitDate' > Version.html
                        """
                    }
                }
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                script {
                    dir("Virtual-Services-MCP-Server") {
                        sh '''
                            python3 --version
                            pip3 --version
                        '''
                    }
                }
            }
        }
        
        stage('Install Dependencies') {
            steps {
                script {
                    dir("Virtual-Services-MCP-Server") {
                        sh '''
                            pip3 install --no-cache-dir . --break-system-packages
                            pip3 install --no-cache-dir pytest pytest-cov --break-system-packages
                        '''
                    }
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    dir("Virtual-Services-MCP-Server") {
                        sh '''
                            mkdir -p reports
                            # Once tests are implemented, run them with:
                            # pytest --junitxml=reports/junit-report.xml --cov=vs_mcp --cov-report=xml:reports/coverage.xml tests/
                            
                            # For now, create empty report to allow pipeline to proceed
                            echo '<?xml version="1.0" encoding="UTF-8"?><testsuites><testsuite name="placeholder" tests="0" errors="0" failures="0" skipped="0"></testsuite></testsuites>' > reports/junit-report.xml
                            echo "Tests will be executed once implemented"
                        '''
                    }
                }
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'Virtual-Services-MCP-Server/reports/junit-report.xml', skipPublishingChecks: true, skipMarkingBuildUnstable: true
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    // Generate base tags
                    tags = getPrDockerDetailedTag(env.CURRENT_BRANCH, checkoutVars.GIT_COMMIT, env.BUILD_NUMBER.toString())
                    
                    // Add branch-specific tags
                    if (env.CURRENT_BRANCH.contains('release')) {
                        tags.addTag('latest-release')
                    }
                    
                    // Only add 'latest' tag for master and develop branches
                    if (env.CURRENT_BRANCH == 'develop' || env.CURRENT_BRANCH == 'master') {
                        tags.addTag('latest')
                    }
                    
                    // Add branch-build tag
                    tags.addTag("${env.CURRENT_BRANCH}-${env.BUILD_NUMBER}")
                    
                    echo "Tags to be applied: ${tags.allTags}"
                    
                    // Convert tag names to full image references for BuildkitManager
                    def fullImageTags = tags.allTags.collect { tag -> 
                        "${env.IMAGE_NAME}:${tag}"
                    }
                    
                    dir("Virtual-Services-MCP-Server") {
                        buildkit.build(
                            dockerFile: "Dockerfile",
                            imageName: env.DOCKER_REPO,
                            tags: fullImageTags,
                            buildArgs: [
                                "BUILD_NUMBER=${env.BUILD_NUMBER}",
                                "BRANCH_NAME=${env.CURRENT_BRANCH}",
                                "BUILD_TIME=${currentBuild.startTimeInMillis}",
                                "COMMIT_HASH=${checkoutVars.GIT_COMMIT}",
                                "CACHEBUST=${currentBuild.startTimeInMillis}" // Force new image per build
                            ]
                        )
                    }
                    
                    // Archive build results
                    def buildManager = new BuildResultManager(this)
                    def buildResult = new PackageBuildResult(env.DOCKER_REPO, tags.allTags[0])
                    buildManager.archiveResultsFromBuildResult(buildResult)
                }
            }
        }
        
        stage('Perform WhiteSource scan') {
            when { expression { return params.PERFORM_WHITESOURCE_SCAN } }
            steps {
                script {
                    def projectName = "Virtual-Services-MCP"
                    def scanComment = "${env.CURRENT_BRANCH}"
                    whiteSourceScan(projectName, scanComment)
                }
            }
        }
        
        stage('Perform PrismaCloud scan') {
            when { expression { return params.PERFORM_PRISMA_SCAN } }
            steps {
                script {
                    TAG = "${env.CURRENT_BRANCH}-${env.BUILD_NUMBER}"
                    runPrismaCloudScanOnK8s(
                        imageTag: "${env.IMAGE_NAME}:${TAG}",
                        buildkitManager: buildkit
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
