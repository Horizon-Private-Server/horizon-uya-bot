REPO=${1}

docker build -t ${REPO} .

aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 062418337237.dkr.ecr.us-west-2.amazonaws.com    
aws ecr create-repository --repository-name ${REPO} --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE
docker tag ${REPO}:latest 062418337237.dkr.ecr.us-west-2.amazonaws.com/${REPO}:latest
docker push 062418337237.dkr.ecr.us-west-2.amazonaws.com/${REPO}:latest  
