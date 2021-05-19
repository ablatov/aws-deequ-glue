# Serverless Data Quality solution based on AWS Deequ and AWS Glue

## Documentation
Original documentation can be found here - https://aws.amazon.com/blogs/big-data/building-a-serverless-data-quality-and-analysis-framework-with-deequ-and-aws-glue/

## Installation & deployment
### From local laptop
1. Setup AWS CLI locally (temporary AWS credentials for the account can be used)
2. Install Python >= 3.7 (check this https://linuxize.com/post/how-to-install-python-3-7-on-ubuntu-18-04/)
3. Install Node.js >= 14.7.0
```
curl -fsSL https://deb.nodesource.com/setup_current.x | sudo -E bash -
sudo apt-get install -y nodejs
```
4. Install needed dependencies 
```
cd backend
make install
mkdir ~/.npm-global
PATH=~/.npm-global/bin:$PATH
NPM_CONFIG_PREFIX=~/.npm-global
sudo npm install -g serverless serverless-pseudo-parameters serverless-python-requirements serverless-wsgi --unsafe
```
5. To deploy simply run:
```
cd ../
./deploy.sh -r $YOUR_REGION_HERE -p $YOUR_AMAZON_PROFILE -n $YOUR_STACK_NAME -e $YOUR_ENV_NAME
```
All these parameters are optional, default values you can find in [deploy.sh](deploy.sh) script.
$YOUR_REGION_HERE - AWS region where you want to deploy 
$YOUR_AMAZON_PROFILE - profile you select to use (set during aws configure)
$YOUR_STACK_NAME - how your Stack will be displayed in AWS Cloudformation
$YOUR_ENV_NAME - environment to deploy resources to (dev\uat\prod)

6. To test the deployment in E2E manner, please use manual from here (Text and links under architecture picture): 
https://aws.amazon.com/blogs/big-data/building-a-serverless-data-quality-and-analysis-framework-with-deequ-and-aws-glue/

### From Jenkins server
1. Build and push docker container with [pushDockerfile.groovy](jenkins/pushDockerfile.groovy)
2. Create a new Jenkins item as a pipeline and use [Jenkinsfile](jenkins/Jenkinsfile) to configure the job.
3. Run Jenkins job with parameters needed.
