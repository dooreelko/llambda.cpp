#!/bin/bash 

set -exu

LLAMA_EXTRA_ARGS=${LLAMA_EXTRA_ARGS:-}

function handler () {
  EVENT_DATA=$1

  NGEN=$(echo "$EVENT_DATA" | jq -r '.["n-generate"]')
  NGEN=${NGEN:-10}

  PROMPT=$(echo "$EVENT_DATA" | jq -r '.prompt')
  if [ -z "$PROMPT" ]; then
    echo "Missing prompt in payload"
    exit 1
  fi

  "$LLAMA_BIN" $LLAMA_EXTRA_ARGS -n "$NGEN" -m "$LLAMA_LOCAL_MODEL" -p "$PROMPT" | tee /dev/stderr
}