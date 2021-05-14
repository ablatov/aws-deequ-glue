properties([
       parameters([
               gitParameter(
                    branch: '',
                    branchFilter: '.*',
                    defaultValue: '',
                    description: 'Repository branches',
                    name: 'BRANCH',
                    quickFilterEnabled: true,
                    sortMode: 'NONE',
                    tagFilter: '*',
                    type: "PT_BRANCH",
                    useRepository: "https://github.com/ablatov/amazon-deequ-glue.git"
               )
       ])
])

node('default-agent') {
    stage('Checkout') {
        checkout([
            $class: 'GitSCM',
            branches: [[name: "${BRANCH}"]],
            doGenerateSubmoduleConfigurations: false,
            extensions: [
                [$class: 'CleanBeforeCheckout']
            ],
            submoduleCfg: [],
            userRemoteConfigs: [[credentialsId: 'creds_id', url: 'https://github.com/ablatov/amazon-deequ-glue.git']]
        ])
    }

    stage("pushDockerfile") {
        env.PATH = """${tool name: 'dock-push-dockerfile', type: 'com.cloudbees.jenkins.plugins.customtools.CustomTool'}:${env.PATH}"""
        pushDockerfile (
            pushDockerfileCredentialsId: 'creds_id',
            pushDockerfileOnlyBuild: false,
            pushDockerfileBuildDir: 'backend'
        )
    }
}