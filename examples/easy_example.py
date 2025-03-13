import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from general_scrisper import general_scrisper
from llm_base import LLMBase

# Example usage
backend_api = "https://api.groq.com/openai/v1"
model = "qwen-2.5-coder-32b"
llm = LLMBase(base_url=backend_api, api_key="")
general_scrisper("Create a function that adds two numbers", llm=llm, model=model, generations=3)

