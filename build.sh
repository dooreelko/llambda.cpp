#!/bin/bash

# If podman build is too slow, you might be using VFS and should use overlayfs instead
# see https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md#ensure-fuse-overlayfs-is-installed


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

mkdir -p ./build
cp --force ./llama.cpp/zig-out/bin/* ./build/

podman build --build-arg LLAMA_MODEL="$MODEL" --file Dockerfile.base --tag llama.base .

IMAGES=(Dockerfile.embed Dockerfile.generate)

for f in "${IMAGES[@]}"; do
    TAG="llama.${f##*.}"
    podman build --file "$f" --tag "$TAG" ./build
    if [ -n "$ECR" ]; then
        ECR_TAG="$ECR:$TAG"
        podman tag "$TAG:latest" "$ECR_TAG"
        podman push "$ECR_TAG"
    fi
done