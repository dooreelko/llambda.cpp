import os
import sys
import logging
from typing import Any, Dict, Iterator, List, Optional

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from pydantic import Field, root_validator
from langchain.schema.output import GenerationChunk
from langchain.utils import get_pydantic_field_names
from langchain.utils.utils import build_extra_kwargs

import requests

logger = logging.getLogger(__name__)

class LlambdaCpp(LLM):
    """llambda.cpp model.

    To use, you should provide the
    url to the Llambda model as a named parameter to the constructor.
    Check out: https://github.com/dooreelko/llambdacpp

    Example:
        .. code-block:: python

            from langchain.llms import LlambdaCpp
            llm = LlambdaCpp(generate_url="https://xxxxxxxxx.lambda-url.eu-central-1.on.aws/", api_key="foobar")
    """

    generate_url: str
    
    api_key: Optional[str]


    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        if not values.get("api_key", ''):
            values["api_key"] = os.environ.get("LLAMA_API_KEY", 'NOKEY')

        if not values.get("api_key", '') or values.get("api_key", '') == 'NOKEY':
            raise ValueError('api_key neither provided in consutructor nor present in the env as LLAMA_API_KEY')

        return values

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "llambdacpp"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the Llambda model and return the output.

        Args:
            prompt: The prompt to use for generation.
            stop: A list of strings to stop generation when encountered.

        Returns:
            The generated text.

        Example:
            .. code-block:: python

                from langchain.llms import LlambdaCpp
                llm = LlambdaCpp(generate_url="https://generate.aws.url.something", api_key="foobar")
                llm("This is a prompt.")
        """

        response = requests.post(self.generate_url, json={
            "prompt": prompt,
            "n-generate": kwargs.get("n-generate", 10),
            "api-key": self.api_key
        }, headers={"content-type": "application/json"})

        if not response.ok:
            print(response.headers, file=sys.stderr)
            response.raise_for_status()

        return response.json()