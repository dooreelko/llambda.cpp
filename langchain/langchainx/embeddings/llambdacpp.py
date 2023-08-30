import os
import sys
from random import randrange

from typing import Any, Dict, List, Optional

from langchain.embeddings.base import Embeddings
from pydantic import BaseModel, Extra, root_validator

import asyncio
import aiohttp

class LlambdaCppEmbeddings(BaseModel, Embeddings):
    """llambda.cpp embedding model.

    This utilises llama.cpp model deployed as an AWS Lambda.
    Check out: https://github.com/dooreelko/llambda.cpp

    Example:
        .. code-block:: python

            from langchain.embeddings import LlambdaCppEmbeddings
            llama = LlambdaCppEmbeddings(embed_url="https://xxxxxxxxx.lambda-url.eu-central-1.on.aws/", api_key="foobar")
            llama.embed_query('hi how are ')

            the api_key is an optional parameter and, if omitted in constructor, will
            be read from LLAMA_API_KEY env variable. If missing also there - error.
    """
    embed_url: str

    api_key: Optional[str]

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid


    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        if not values.get("api_key", ''):
            values["api_key"] = os.environ.get("LLAMA_API_KEY", 'NOKEY')

        if not values.get("api_key", '') or values.get("api_key", '') == 'NOKEY':
            raise ValueError('api_key neither provided in consutructor nor present in the env as LLAMA_API_KEY')

        return values

    async def _run_one_async(self, session: aiohttp.ClientSession, text: str, idx: int, dones: List[int], num_tasks: int) -> List[float]:
        async with session.post(self.embed_url,
            json={
                "prompt": text,
                "n-generate": 10,
                "api-key": self.api_key
            }, 
            headers={"content-type": "application/json"}) as response:        
            if not response.ok:
                print(response.headers, file=sys.stderr)
                response.raise_for_status()

            result = await response.json()
            dones.append(idx)
            print(f"done {int(len(dones)/num_tasks*100)}%", file=sys.stderr, end='\r', flush=True)

            return result
        
    async def _embed_multi(self, texts: List[str]) -> List[List[float]]:

        # 15 minutes max lambda execution duration
        # while the aiohttp default is 300s
        timeout = aiohttp.ClientTimeout(total=15*60) 
        session = aiohttp.ClientSession(timeout=timeout)
        dones = []
        tasks = [self._run_one_async(session, text, idx, dones, len(texts)) for idx,text in enumerate(texts)]

        results = await asyncio.gather(*tasks)

        await session.close()

        return results


    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        print(f"multi embed {len(texts)}", file=sys.stderr)

        return asyncio.run(self._embed_multi(texts))
        
    def embed_query(self, text: str) -> List[float]:
        print("single embed", file=sys.stderr)

        return asyncio.run(self._embed_multi([text]))[0]
