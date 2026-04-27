# Copyright (c) 2026 Jasper Kleine — Licensed under the MIT License. See LICENSE-SECOND.
import os
import time

import dotenv
from google import genai

from .Base import BaseModel

dotenv.load_dotenv()


class Gemini(BaseModel):
    def __init__(self, temperature=0, model_name: str = "gemini-pro"):
        # Create a genai Client
        api_key = os.getenv("Google_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else genai.Client()
        self.model_name = model_name

    # @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    def prompt(self, processed_input):
        contents = processed_input[0]["content"]
        response = None
        for _ in range(10):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                )
                return response.text, 0, 0
            except Exception:
                time.sleep(2)

        if response is not None:
            return response.text, 0, 0
