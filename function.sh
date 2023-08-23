#!/bin/bash 

set -exu

LLAMA_SECRET=${LLAMA_SECRET:-}
LLAMA_EXTRA_ARGS=${LLAMA_EXTRA_ARGS:-}

function handler () {
  EVENT_DATA=$1

  APIKEY=$(echo "$EVENT_DATA" | jq -r '.["api-key"]')

  if [ -z "$LLAMA_SECRET" ]; then 
    echo '{"errorMessage" : "Missing API secret in LLAMA_SECRET.", "errorType" : "ServerError"}'
    exit 
  fi

  if [ "$APIKEY" != "$LLAMA_SECRET" ]; then 
    echo '{"errorMessage" : "Wrong or missing API key.", "errorType" : "Unauthorised"}'
    exit 
  fi

  NGEN=$(echo "$EVENT_DATA" | jq -r '.["n-generate"]')
  NGEN=${NGEN:-10}

  PROMPT=$(echo "$EVENT_DATA" | jq -r '.prompt')
  if [ -z "$PROMPT" ]; then
    echo '{"errorMessage" : "Missing prompt in payload.", "errorType" : "BadRequest"}'
    exit 
  fi

  "$LLAMA_BIN" $LLAMA_EXTRA_ARGS -n "$NGEN" -m "$LLAMA_LOCAL_MODEL" -p "$PROMPT" | tee /dev/stderr
}