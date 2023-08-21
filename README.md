# Run llama.cpp as a lambda function on aws

## Deployment

1. Create an ECR repo and log in into it using docker. Something like
   `aws ecr get-login-password --region eu-central-1 | podman login --username AWS --password-stdin XXXXXXXX.dkr.ecr.eu-central-1.amazonaws.com`

2. create an `.ecr-env` file containing target repo in form of

```
ECR='XXXXXXXX.dkr.ecr.eu-central-1.amazonaws.com/XXXREPOXXX'
```

3. Run `./build.sh` this will build images and deploy them to ECR

4. Create the lambda functions from the images

5. Test using payload like `{"prompt": "llamas are", "n-generate": 1}`. Where
   `n-generate` is number of tokens to generate.

## Caveats

First execution takes about 10-15 minutes for the model to end up in the "hot"
storage. Subsequent executions take time proportionate to the n-generate,
roughly 2 tokens per second.
