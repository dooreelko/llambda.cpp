#!/bin/bash

set -exuo pipefail

if [ ! -f .ecr-env ]; then
    echo "Missing .ecr-env"

    exit 1
fi

source .ecr-env

FUNCTIONS=(embed generate)

for f in "${FUNCTIONS[@]}"; do
    aws lambda update-function-code --function-name llama-"$f" --image-uri "$ECR":llama."$f"
done

while true; do
    IN_PROGRESS=''

    for f in "${FUNCTIONS[@]}"; do
        STATUS=$(aws lambda get-function --function-name llama-"$f" | jq -r .Configuration.LastUpdateStatus)

        if [ "$STATUS" != 'Successful' ]; then
            IN_PROGRESS='aye'

            echo "llama-$f is still in $STATUS"

            sleep 10
            break
        fi
    done

    [[ -n "$IN_PROGRESS" ]] || break

done