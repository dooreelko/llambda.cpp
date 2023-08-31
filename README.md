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

## Cost

Assuming lambda functions configured as:

- pricing is for eu-central-1 region
- 8000Mb RAM (to fit 7B llama model)
- X86 architecture
- Max duration 15 minutes
- Avergate duration for embedding of a 512-token snippet 6000ms

You can expect making 8539 lambda invocations without leaving the free tier.
After that every 100'000 invocations will cost $78.15 USD ($0.00007815 per
request), with a breakdown of

```
Unit conversions

    Amount of memory allocated: 8000 MB x 0.0009765625 GB in a MB = 7.8125 GB
    Amount of ephemeral storage allocated: 512 MB x 0.0009765625 GB in a MB = 0.5 GB

Pricing calculations
100,000 requests x 6,000 ms x 0.001 ms to sec conversion factor = 600,000.00 total compute (seconds)
7.8125 GB x 600,000.00 seconds = 4,687,500.00 total compute (GB-s)
4,687,500.00 GB-s x 0.0000166667 USD = 78.13 USD (monthly compute charges)
100,000 requests x 0.0000002 USD = 0.02 USD (monthly request charges)
0.50 GB - 0.5 GB (no additional charge) = 0.00 GB billable ephemeral storage per function
78.13 USD + 0.02 USD = 78.15 USD
Lambda costs - Without Free Tier (monthly): 78.15 USD
```

Keep in mind, that generation requests have a greater variability in time
duration (especially since they depend on n-generate parameter), so the number
of requests will be likely smaller for the same price.
