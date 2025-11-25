@Library('jenkins_library')
import com.blazemeter.buildkit.BuildkitManager
import com.blazemeter.pr.PullRequestUtils
import com.blazemeter.pr.PullRequestStatus
import com.blazemeter.pr.PackageBuildResult
import com.blazemeter.pr.BuildResultManager

BuildkitManager buildkit = new BuildkitManager(this)

DOCKER_REPO = 'vs-mcp'
IMAGE_NAME = 'gcr.io/verdant-bulwark-278/vs-mcp'
def isCodeScan = isCodeScan()
def podYaml = libraryResource 'podTemplates/jenkins-docker-agent-master-latest.yaml'

properties([pipelineTriggers([githubPush()])]) //Enable Git webhook triggering

pipeline {
    parameters {
        booleanParam(name: 'PERFORM_PRISMA_SCAN', defaultValue: true, description: 'Perform a Prisma scan for the Docker image')
        booleanParam(name: 'FAIL_JOB_ON_SCAN_FAILURES', defaultValue: false, description: 'If checked, Twistlock vulnerabilities scan will enforce job failure.')
        booleanParam(name: 'PERFORM_WHITESOURCE_SCAN', defaultValue: isCodeScan, description: 'Perform a WhiteSource scan for the code')
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '100', daysToKeepStr: '45'))
        ansiColor('xterm')
        timestamps()
        disableConcurrentBuilds()
    }

    agent {
        kubernetes {
            yaml podYaml
            defaultContainer 'jenkins-docker-agent'
            workspaceVolume dynamicPVC(accessModes: 'ReadWriteOnce', requestsSize: "5Gi", storageClassName: "standard-rwo")
        }
    }
    
    environment {
        project = 'Virtual-Services-MCP-Server'
        TMPDIR = '/tmp'
        SENDER = 'jenkins@blazemeter.com'
    }
    
    stages {
        stage('Setup') {
            steps {
                script {
                    PullRequestUtils.updateBranchPullRequestsStatuses(this, PullRequestStatus.PENDING)
                    env.MODIFIED_BUILD_NUMBER = env.BUILD_NUMBER
                    currentBuild.displayName = "#${MODIFIED_BUILD_NUMBER} | [Node] ${env.NODE_NAME} | ${env.BRANCH_NAME}"
                }
            }
        }
        
        stage('Clone') {
            steps {
                script {
                    clearWorkspace()
                    checkoutVars = repositoryDirectoryCheckout('Virtual-Services-MCP-Server', 'Virtual-Services-MCP-Server', env.BRANCH_NAME)
                    allowSafeDir = sh script: 'git config --global --add safe.directory "*"', returnStdout: true
                    dir("Virtual-Services-MCP-Server") {
                        commitDate = sh script: 'git log -1 --format="%ad %H"', returnStdout: true
                        sh """
                            echo -n '$JOB_NAME $BUILD_NUMBER $env.BRANCH_NAME $checkoutVars.GIT_COMMIT $commitDate' > Version.html
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
                    dir("Virtual-Services-MCP-Server") {
                        buildkit.build(
                            dockerFile: "Dockerfile",
                            imageName: DOCKER_REPO,
                            buildArgs: [
                                "BUILD_NUMBER=${env.BUILD_NUMBER}",
                                "BRANCH_NAME=${env.BRANCH_NAME}",
                                "BUILD_TIME=${currentBuild.startTimeInMillis}",
                                "COMMIT_HASH=${checkoutVars.GIT_COMMIT}"
                            ]
                        )
                    }
                }
            }
        }
        
        stage('Push to Registry') {
            steps {
                script {
                    tags = getPrDockerDetailedTag(env.BRANCH_NAME, checkoutVars.GIT_COMMIT, env.BUILD_NUMBER.toString())
                    
                    if (env.BRANCH_NAME.contains('release')) {
                        tags.addTag('latest-release')
                    }
                    if (env.BRANCH_NAME == 'develop' || env.BRANCH_NAME == 'master') {
                        tags.addTag('latest')
                    }
                    tags.addTag(BUILD_NUMBER.toString())
                    tags.addTag("${env.BRANCH_NAME}-${env.BUILD_NUMBER}")
                    
                    lock(label: 'Gcloud-VS-MCP') {
                        pushImageToAllRegistries(DOCKER_REPO, DOCKER_REPO, tags, buildkit)
                    }
                    
                    def buildManager = new BuildResultManager(this)
                    def buildResult = new PackageBuildResult(DOCKER_REPO, tags.allTags[0])
                    buildManager.archiveResultsFromBuildResult(buildResult)
                }
            }
        }
        
        stage('Perform WhiteSource scan') {
            when { expression { return params.PERFORM_WHITESOURCE_SCAN } }
            steps {
                script {
                    def projectName = "Virtual-Services-MCP"
                    def scanComment = "${env.BRANCH_NAME}"
                    whiteSourceScan(projectName, scanComment)
                }
            }
        }
        
        stage('Perform PrismaCloud scan') {
            when { expression { return params.PERFORM_PRISMA_SCAN } }
            steps {
                script {
                    TAG = "${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
                    runPrismaCloudScanOnK8s(
                        imageTag: "${IMAGE_NAME}:${TAG}",
                        buildkitManager: buildkit
                    )
                }
            }
        }
    }
    
    post {
        always {
            smartSlackNotification(alternateJobTitle: 'VS-MCP package build')
            script {
                buildkit.cleanup()
                if (!env.skippedBuild) {
                    PullRequestUtils.updateBranchPullRequestsStatuses(this)
                }
            }
        }
        failure {
            notifyJobFailureEmailToAuthor(sender: 'jenkins@blazemeter.com')
        }
    }
}
