# Serverless Data Quality solution based on AWS Deequ and AWS Glue

## Documentation
Original documentation can be found here - https://aws.amazon.com/blogs/big-data/building-a-serverless-data-quality-and-analysis-framework-with-deequ-and-aws-glue/

## Installation & deployment
### From local laptop
1. Setup AWS CLI locally (temporary AWS credentials for the account can be used)
2. Install Python >= 3.7
3. Install Node.js >= 14.7.0
4. To deploy simply run:
```
./deploy.sh -r $YOUR_REGION_HERE -p $YOUR_AMAZON_PROFILE -n $YOUR_STACK_NAME -e $YOUR_ENV_NAME
```

### From Jenkins server
1. Build and push docker container with [pushDockerfile.groovy](jenkins/pushDockerfile.groovy)
2. Create a new Jenkins item as a pipeline and use [Jenkinsfile](jenkins/Jenkinsfile) to configure the job.
3. Run Jenkins job with parameters needed.
