import time
from typing import Any, Optional

from deepeval.models import DeepEvalBaseLLM
from deepeval.models.llms.utils import trim_and_load_json
from groq import Groq


class GroqModel(DeepEvalBaseLLM):

    def __init__(self, api_key, model="llama-3.1-8b-instant"):
        self.client = Groq(api_key=api_key)
        self.model = model

    def load_model(self):
        return self.client

    def get_model_name(self):
        return self.model

    def generate(self, prompt: str, schema: Optional[Any] = None, **kwargs) -> Any:
        request_kwargs = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "max_tokens": 1024,
        }

        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(**request_kwargs)
                break
            except Exception as e:
                if "429" in str(e) and attempt < 2:
                    time.sleep(30)
                else:
                    raise

        output = response.choices[0].message.content

        if schema is not None:
            json_output = trim_and_load_json(output)
            return schema.model_validate(json_output)

        return output

    async def a_generate(self, prompt: str, schema: Optional[Any] = None, **kwargs) -> Any:
        return self.generate(prompt, schema=schema, **kwargs)

    def supports_json_mode(self) -> bool:
        return False
