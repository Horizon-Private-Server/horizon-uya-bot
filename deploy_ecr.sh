REPO=${1}

#!/bin/bash

# Fetch temporary credentials
TEMP_CREDENTIALS=$(aws sts get-session-token --duration-seconds 3600)

echo $TEMP_CREDENTIALS

# Extract credentials using jq
AWS_ACCESS_KEY_ID=$(echo $TEMP_CREDENTIALS | jq -r '.Credentials.AccessKeyId')
AWS_SECRET_ACCESS_KEY=$(echo $TEMP_CREDENTIALS | jq -r '.Credentials.SecretAccessKey')
AWS_SESSION_TOKEN=$(echo $TEMP_CREDENTIALS | jq -r '.Credentials.SessionToken')

# Export the credentials as environment variables
export AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY
export AWS_SESSION_TOKEN

echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
echo $AWS_SESSION_TOKEN


docker build --platform="linux/amd64" -t ${REPO} .

aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 062418337237.dkr.ecr.us-west-2.amazonaws.com    
aws ecr create-repository --repository-name ${REPO} --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE
docker tag ${REPO}:latest 062418337237.dkr.ecr.us-west-2.amazonaws.com/${REPO}:latest
docker push 062418337237.dkr.ecr.us-west-2.amazonaws.com/${REPO}:latest  
