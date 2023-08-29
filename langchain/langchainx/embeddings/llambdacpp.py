import os
import sys

from typing import Any, Dict, List, Optional

from langchain.embeddings.base import Embeddings
from pydantic import BaseModel, Extra, root_validator

import asyncio
import requests

class LlambdaCppEmbeddings(BaseModel, Embeddings):
    """llama.cpp embedding models.

    To use, you should have the llama-cpp-python library installed, and provide the
    path to the Llama model as a named parameter to the constructor.
    Check out: https://github.com/abetlen/llama-cpp-python

    Example:
        .. code-block:: python

            from langchain.embeddings import LlambdaCppEmbeddings
            llama = LlambdaCppEmbeddings(embed_url="https://address.of.the.lambda/embed", api_key="foobar")
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

    def _run_one(self, text: str) -> List[float]:
        response = requests.post(self.embed_url, 
            json={
                "prompt": text,
                "n-generate": 10,
                "api-key": self.api_key
            }, 
            headers={"content-type": "application/json"})

        if not response.ok:
            print(response.headers, file=sys.stderr)
            response.raise_for_status()

        return response.json()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
            return [self._run_one(text) for text in texts]
    
    # async def embed_documents(self, texts: List[str]) -> List[List[float]]:
    #     async with asyncio.TaskGroup() as tg:
    #         tasks = [tg.create_task(self._run_one([text])) for text in texts]

    #         loop = asyncio.get_event_loop()
    #         results = loop.run_until_complete(asyncio.wait(tasks))
    #         loop.close()

    #         return results
    
    def embed_query(self, text: str) -> List[float]:

        return self._run_one(text)