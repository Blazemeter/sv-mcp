@Library('jenkins_library')
import com.blazemeter.buildkit.BuildkitManager
import com.blazemeter.pr.PullRequestUtils

BuildkitManager buildkit = new BuildkitManager(this)

pipeline {
    agent {
        kubernetes {
            yaml agentYaml()
            defaultContainer 'jenkins-docker-agent'
            workspaceVolume dynamicPVC(accessModes: 'ReadWriteOnce', requestsSize: "5Gi", storageClassName: "standard-rwo")
            retries 2
        }
    }

    parameters {
        booleanParam(name: 'PERFORM_PRISMACLOUD_SCAN', defaultValue: true, description: 'Perform PrismaCloud security scan on Docker image')
        booleanParam(name: 'PERFORM_WHITESOURCE_SCAN', defaultValue: true, description: 'Perform WhiteSource scan for dependencies')
        booleanParam(name: 'SKIP_TESTS', defaultValue: false, description: 'Skip running tests')
    }

    environment {
        DOCKER_IMAGE_NAME = 'vs-mcp'
        DOCKER_REGISTRY = 'gcr.io/verdant-bulwark-278'
        PROJECT_NAME = 'virtual-services-mcp'
        PYTHON_VERSION = '3.12'
        // Version file path
        VERSION_FILE = 'pyproject.toml'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '30', daysToKeepStr: '30'))
        timestamps()
        timeout(time: 1, unit: 'HOURS')
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    cleanCheckout()
                    
                    // Determine if this is a PR build
                    env.IS_PR = env.CHANGE_ID ? 'true' : 'false'
                    echo "Is Pull Request: ${env.IS_PR}"
                    echo "Branch: ${env.BRANCH_NAME}"
                }
            }
        }

        stage('Setup Python Environment') {
            steps {
                script {
                    echo "Setting up Python ${PYTHON_VERSION} environment"
                    sh '''
                        python3 --version
                        pip3 --version
                    '''
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    echo "Installing project dependencies"
                    sh '''
                        pip3 install --no-cache-dir . --break-system-packages
                        pip3 install --no-cache-dir pytest pytest-cov --break-system-packages
                    '''
                }
            }
        }

        stage('Run Tests') {
            when {
                expression { return !params.SKIP_TESTS }
            }
            steps {
                script {
                    echo "Running tests..."
                    sh '''
                        mkdir -p reports
                        # Once tests are implemented, run them with:
                        # pytest --junitxml=reports/junit-report.xml --cov=vs_mcp --cov-report=xml:reports/coverage.xml --cov-report=html:reports/htmlcov tests/
                        
                        # For now, create empty report to allow pipeline to proceed
                        echo '<?xml version="1.0" encoding="UTF-8"?><testsuites><testsuite name="placeholder" tests="0" errors="0" failures="0" skipped="0"></testsuite></testsuites>' > reports/junit-report.xml
                        echo "Tests will be executed once implemented"
                    '''
                }
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/junit-report.xml', skipPublishingChecks: true, skipMarkingBuildUnstable: true
                }
            }
        }

        stage('Determine Version') {
            steps {
                script {
                    if (env.BRANCH_NAME == 'master') {
                        // Auto-increment version for master branch builds
                        def currentVersion = sh(
                            script: "grep '^version = ' ${VERSION_FILE} | sed 's/version = \"\\(.*\\)\"/\\1/'",
                            returnStdout: true
                        ).trim()
                        
                        echo "Current version: ${currentVersion}"
                        
                        // Parse version and increment patch
                        def versionParts = currentVersion.tokenize('.')
                        def major = versionParts[0]
                        def minor = versionParts.size() > 1 ? versionParts[1] : '0'
                        def patch = versionParts.size() > 2 ? versionParts[2].toInteger() + 1 : env.BUILD_NUMBER
                        
                        env.IMAGE_VERSION = "${major}.${minor}.${patch}"
                        env.DOCKER_TAGS = "${env.IMAGE_VERSION},latest"
                        
                        echo "New version for master: ${env.IMAGE_VERSION}"
                        
                        // Update version in pyproject.toml
                        sh """
                            sed -i 's/^version = .*/version = "${env.IMAGE_VERSION}"/' ${VERSION_FILE}
                            git config user.email "jenkins@blazemeter.com"
                            git config user.name "Jenkins CI"
                            git add ${VERSION_FILE}
                            git diff --staged --quiet || git commit -m "Bump version to ${env.IMAGE_VERSION} [skip ci]"
                        """
                    } else if (env.IS_PR == 'true') {
                        // For PRs, use PR number in version
                        env.IMAGE_VERSION = "pr-${env.CHANGE_ID}-${env.BUILD_NUMBER}"
                        env.DOCKER_TAGS = env.IMAGE_VERSION
                        echo "PR version: ${env.IMAGE_VERSION}"
                    } else {
                        // For feature branches, use branch name and build number
                        def safeBranchName = env.BRANCH_NAME.replaceAll('[^a-zA-Z0-9]', '-').toLowerCase()
                        env.IMAGE_VERSION = "${safeBranchName}-${env.BUILD_NUMBER}"
                        env.DOCKER_TAGS = env.IMAGE_VERSION
                        echo "Branch version: ${env.IMAGE_VERSION}"
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image with tags: ${env.DOCKER_TAGS}"
                    
                    def tags = env.DOCKER_TAGS.split(',').collect { 
                        "${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:${it}" 
                    }
                    
                    buildkit.build(
                        dockerFile: "Dockerfile",
                        imageName: DOCKER_IMAGE_NAME,
                        tags: tags,
                        buildArgs: [
                            "BUILD_NUMBER=${env.BUILD_NUMBER}",
                            "BRANCH_NAME=${env.BRANCH_NAME}",
                            "BUILD_TIME=${currentBuild.startTimeInMillis}",
                            "COMMIT_HASH=${env.GIT_COMMIT}"
                        ]
                    )
                    
                    // Store the primary tag for later stages
                    env.PRIMARY_IMAGE_TAG = "${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:${env.IMAGE_VERSION}"
                }
            }
        }

        stage('Perform PrismaCloud Scan') {
            when { 
                expression { 
                    return params.PERFORM_PRISMACLOUD_SCAN 
                } 
            }
            steps {
                script {
                    echo "Running PrismaCloud security scan on ${env.PRIMARY_IMAGE_TAG}"
                    runPrismaCloudScanOnK8s(
                        imageTag: env.PRIMARY_IMAGE_TAG,
                        buildkitManager: buildkit
                    )
                }
            }
        }

        stage('Perform WhiteSource Scan') {
            when { 
                expression { 
                    return params.PERFORM_WHITESOURCE_SCAN 
                } 
            }
            steps {
                script {
                    echo "Running WhiteSource scan"
                    def projectName = PROJECT_NAME
                    whiteSourceScan(projectName)
                }
            }
        }

        stage('Push Docker Image') {
            when {
                expression { 
                    // Only push to registry from master or when explicitly needed
                    return env.BRANCH_NAME == 'master' || env.IS_PR == 'false'
                }
            }
            steps {
                script {
                    echo "Pushing Docker image(s) to ${DOCKER_REGISTRY}"
                    
                    env.DOCKER_TAGS.split(',').each { tag ->
                        def fullTag = "${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:${tag}"
                        buildkit.push(fullTag)
                        echo "Pushed: ${fullTag}"
                    }
                }
            }
        }

        stage('Commit Version Update') {
            when {
                expression { return env.BRANCH_NAME == 'master' }
            }
            steps {
                script {
                    echo "Pushing version update to repository"
                    sh '''
                        git push origin HEAD:master
                    '''
                }
            }
        }

        stage('Update PR Status') {
            when {
                expression { return env.IS_PR == 'true' }
            }
            steps {
                script {
                    // Update PR with build information
                    echo "Build completed for PR #${env.CHANGE_ID}"
                    echo "Docker image: ${env.PRIMARY_IMAGE_TAG}"
                }
            }
        }
    }

    post {
        success {
            script {
                def message = "✅ Build Successful\n"
                message += "Branch: ${env.BRANCH_NAME}\n"
                message += "Version: ${env.IMAGE_VERSION}\n"
                if (env.BRANCH_NAME == 'master' || env.IS_PR == 'false') {
                    message += "Image: ${env.PRIMARY_IMAGE_TAG}\n"
                }
                echo message
            }
        }
        failure {
            script {
                def message = "❌ Build Failed\n"
                message += "Branch: ${env.BRANCH_NAME}\n"
                message += "Check console output for details"
                echo message
            }
        }
        always {
            script {
                // Cleanup
                echo "Cleaning up workspace"
                cleanWs()
            }
        }
    }
}
