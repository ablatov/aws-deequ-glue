#!/bin/bash
nflag=false
pflag=false
rflag=false
eflag=false

DIRNAME=$(pwd)

usage () { echo "
    -h -- Opens up this help message
    -n -- Name of the CloudFormation stack
    -p -- Name of the AWS profile to use
    -r -- AWS Region to use
    -e -- Name of the environment
"; }
options=':n:p:r:e:dh'
while getopts $options option
do
    case "$option" in
        n  ) nflag=true; STACK_NAME=$OPTARG;;
        p  ) pflag=true; PROFILE=$OPTARG;;
        r  ) rflag=true; REGION=$OPTARG;;
        e  ) eflag=true; ENV=$OPTARG;;
        h  ) usage; exit;;
        \? ) echo "Unknown option: -$OPTARG" >&2; exit 1;;
        :  ) echo "Missing option argument for -$OPTARG" >&2; exit 1;;
        *  ) echo "Unimplemented option: -$OPTARG" >&2; exit 1;;
    esac
done

if ! $pflag
  then
      echo "-p not specified, will not use this option" >&2
      PROFILE=""
else
  AWS_CLI_PROFILE="--profile $PROFILE"
  SLS_PROFILE="--aws-profile $PROFILE"
fi
if ! $nflag
then
    STACK_NAME="serverless-data-quality-deequ-glue"
fi
if ! $rflag
then
    echo "-r not specified, using default us-east-1..." >&2
    REGION='us-east-1'
fi
if ! $eflag
then
    echo "-e not specified, using dev..." >&2
    ENV="dev"
fi

ACCOUNT=$(aws sts get-caller-identity --query 'Account' --output text $AWS_CLI_PROFILE)
echo "## CURRENT STAGE ##: Creating CloudFormation Artifacts Bucket..."
S3_BUCKET=amazon-deequ-glue-$REGION-$ACCOUNT
WEB_UI_S3_BUCKET=data-quality-web-$REGION-$ACCOUNT

if ! aws s3 ls $S3_BUCKET $AWS_CLI_PROFILE; then
  echo "S3 bucket named $S3_BUCKET does not exist. Creating."
  aws s3 mb s3://$S3_BUCKET --region $REGION $AWS_CLI_PROFILE
  aws ssm put-parameter --region $REGION $AWS_CLI_PROFILE --name "/DataQuality/S3/ArtifactsBucket" --value $S3_BUCKET --type String --overwrite
  aws s3api put-bucket-encryption $AWS_CLI_PROFILE \
    --bucket $S3_BUCKET \
    --server-side-encryption-configuration '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'
  aws s3api put-public-access-block $AWS_CLI_PROFILE \
    --bucket $S3_BUCKET \
    --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
else
  echo "Bucket $S3_BUCKET exists already."
fi

mkdir $DIRNAME/output
aws cloudformation package $AWS_CLI_PROFILE --region $REGION --template-file $DIRNAME/template.yaml \
  --s3-bucket $S3_BUCKET --s3-prefix deequ/templates --output-template-file $DIRNAME/output/packaged-template.yaml

echo "## CURRENT STAGE ##: Checking if stack exists ..."
if ! aws cloudformation describe-stacks $AWS_CLI_PROFILE --region $REGION --stack-name $STACK_NAME; then

  echo -e "Stack does not exist, creating ..."
  aws cloudformation create-stack $AWS_CLI_PROFILE \
    --region $REGION \
    --stack-name $STACK_NAME \
    --template-body file://$DIRNAME/output/packaged-template.yaml \
    --parameters \
      ParameterKey=pArtifactsBucket,ParameterValue=$S3_BUCKET \
      ParameterKey=pEnv,ParameterValue=$ENV \
    --tags file://$DIRNAME/tags.json \
    --capabilities "CAPABILITY_NAMED_IAM" "CAPABILITY_AUTO_EXPAND"

  echo "Waiting for stack to be created ..."
  aws cloudformation wait stack-create-complete $AWS_CLI_PROFILE --region $REGION \
    --stack-name $STACK_NAME
else
  echo -e "Stack exists, attempting update ..."

  set +e
  update_output=$(aws cloudformation update-stack $AWS_CLI_PROFILE \
    --region $REGION \
    --stack-name $STACK_NAME \
    --template-body file://$DIRNAME/output/packaged-template.yaml \
    --parameters \
      ParameterKey=pArtifactsBucket,ParameterValue=$S3_BUCKET \
      ParameterKey=pEnv,ParameterValue=$ENV \
    --tags file://$DIRNAME/tags.json \
    --capabilities "CAPABILITY_NAMED_IAM" "CAPABILITY_AUTO_EXPAND" 2>&1)
  status=$?
  set -e

  echo "$update_output"

  if [ $status -ne 0 ] ; then
    # Don't fail for no-op update
    if [[ $update_output == *"ValidationError"* && $update_output == *"No updates"* ]] ; then
      echo -e "\nFinished create/update - no updates to be performed";
      exit 0;
    else
      exit $status
    fi
  fi

  echo "Waiting for stack update to complete ..."
  aws cloudformation wait stack-update-complete $AWS_CLI_PROFILE --region $REGION \
    --stack-name $STACK_NAME
  echo "Finished create/update successfully!"
fi

echo "## CURRENT STAGE ##: Loading Deequ scripts to S3 bucket..."
aws s3 sync ./main/scala/deequ/ s3://$S3_BUCKET/deequ/scripts/ $AWS_CLI_PROFILE
aws s3 cp ./main/resources/deequ-1.0.3-RC1.jar s3://$S3_BUCKET/deequ/jars/ $AWS_CLI_PROFILE
aws s3 cp ./main/utils/deequ-controller/deequ-controller.py s3://$S3_BUCKET/deequ/scripts/ $AWS_CLI_PROFILE

echo "## CURRENT STAGE ##: Deploy REST API and Lambda with Serverless..."
cd ./backend
sls deploy --stage $ENV --region $REGION --verbose $SLS_PROFILE
API_URL="$(sls info --verbose | grep ServiceEndpoint | sed s/ServiceEndpoint\:\ //g)"

echo "## CURRENT STAGE ##: Put dummy index.html to S3 bucket for further Cognito configuration..."
touch index.html
aws s3 cp ./index.html s3://$WEB_UI_S3_BUCKET/

echo "## CURRENT STAGE ##: Configuring Congito App client..."
USER_POOL_ID="$(aws cognito-idp list-user-pools --max-results 1 --output text $AWS_CLI_PROFILE | awk -F " " '{print $3}' | xargs)"
APP_CLIENT_ID="$(aws cognito-idp list-user-pool-clients --user-pool-id $USER_POOL_ID --output text $AWS_CLI_PROFILE | awk -F " " '{print $2}' | xargs)"
WEB_URL="https://$WEB_UI_S3_BUCKET.s3.amazonaws.com/index.html"
aws cognito-idp update-user-pool-client --user-pool-id $USER_POOL_ID --client-id $APP_CLIENT_ID \
  --allowed-o-auth-flows-user-pool-client --allowed-o-auth-flows "code" "implicit" \
  --allowed-o-auth-scopes "openid" "email" "phone" "profile" \
  --callback-urls '["'"$WEB_URL"'"]' \
  --logout-urls '["'"$WEB_URL"'"]' \
  --supported-identity-providers "COGNITO" $AWS_CLI_PROFILE

RANDOM_UUID=$(cat /dev/urandom | env LC_CTYPE=C tr -dc 'a-zA-Z' | fold -w 5 | head -n 1)
DEMO_USERNAME="$RANDOM_UUID@domain.com"
DEMO_PASS="123aA$RANDOM_UUID"
aws cognito-idp admin-create-user --user-pool-id $USER_POOL_ID --username $DEMO_USERNAME --temporary-password $DEMO_PASS

echo "## CURRENT STAGE ##: Rebuild Web UI and redeploy to S3 bucket..."
echo "Building with variables: REACT_APP_BASE_URL=$API_URL REACT_APP_USER_POOL_ID=$USER_POOL_ID REACT_APP_APP_CLIENT_ID=$APP_CLIENT_ID REACT_APP_REGION=$REGION"
cd ../web_ui && npm install -f
REACT_APP_BASE_URL=$API_URL REACT_APP_USER_POOL_ID=$USER_POOL_ID REACT_APP_APP_CLIENT_ID=$APP_CLIENT_ID REACT_APP_REGION=$REGION npm run build
aws s3 cp ./build s3://$WEB_UI_S3_BUCKET/ $AWS_CLI_PROFILE --recursive

echo "To verify the installation, please go to $WEB_URL and login with username: $DEMO_USERNAME password: $DEMO_PASS"
