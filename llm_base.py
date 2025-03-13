import os
from typing import Dict, List, Optional, Union, Any
from openai import OpenAI

class LLMBase:
    """
    A base class for interacting with OpenAI-compatible LLM APIs.
    Allows for custom backend URLs and API keys.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initialize the LLM client with custom settings.
        
        """

        # Use provided values or fall back to environment variables
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = base_url or os.environ.get("OPENAI_BASE_URL")
        
        if not self.api_key:
            raise ValueError("API key must be provided as parameter or OPENAI_API_KEY environment variable")
            
        # Initialize OpenAI client with appropriate parameters
        # Pass parameters directly to avoid type errors with **kwargs unpacking
        if self.base_url:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            self.client = OpenAI(api_key=self.api_key)
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate a chat completion response.
        
        Args:
            messages: List of message objects (role, content)
            model: Override default model
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            **kwargs: Additional parameters to pass to the API
            
        Returns:
            The text response from the model
        """
        # Use instance defaults unless overridden
        # Only include max_tokens if it's specified
        completion_kwargs = {
            "model": model,
            "temperature": temperature,
            "messages": messages,
            **kwargs
        }
        
        try:
            response = self.client.chat.completions.create(**completion_kwargs)
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error in chat completion: {str(e)}")
    
    