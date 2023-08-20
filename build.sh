#!/bin/bash

set -exuo pipefail

if [ -f .ecr-env ]; then
    source .ecr-env
fi

ECR=${ECR:-}

MODEL=${MODEL:-}

if [ -z "$MODEL" ]; then
    MODEL=$(find ./model -maxdepth 1 -iname '*bin' | head -n1)
fi

if [ -z "$MODEL" ]; then
    echo "No model bin files found and none provided in MODEL env var"
    exit 1
fi

docker build --file Dockerfile.build --tag llama.build ./llama.cpp

docker build --build-arg LLAMA_MODEL="$MODEL" --file Dockerfile.base --tag llama.base .

IMAGES=(Dockerfile.embed Dockerfile.generate)

for f in "${IMAGES[@]}"; do
    TAG="llama.${f##*.}"
    docker build --file "$f" --tag "$TAG" ./empty
    if [ -n "$ECR" ]; then
        ECR_TAG="$ECR:$TAG"
        docker tag "$TAG:latest" "$ECR_TAG"
        docker push "$ECR_TAG"
    fi
done