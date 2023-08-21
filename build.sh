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

podman build --build-arg NO_CACHE="$RANDOM" --file Dockerfile.build --tag llama.build -v "$PWD":/work:rw .

podman build --build-arg LLAMA_MODEL="$MODEL" --file Dockerfile.base --tag llama.base .

IMAGES=(Dockerfile.embed Dockerfile.generate)

for f in "${IMAGES[@]}"; do
    TAG="llama.${f##*.}"
    podman build --file "$f" --tag "$TAG" ./empty
    if [ -n "$ECR" ]; then
        ECR_TAG="$ECR:$TAG"
        podman tag "$TAG:latest" "$ECR_TAG"
        podman push "$ECR_TAG"
    fi
done