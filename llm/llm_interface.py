import os
import json
from openai import OpenAI


class LLMInterface:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )

    def generate_tasks(self, goal):
        prompt = f"""
        Break down the following goal into structured actionable tasks.

        Return ONLY valid JSON in this format:

        [
          {{
            "id": "T1",
            "name": "Task name",
            "dependencies": []
          }}
        ]

        Goal:
        {goal}
        """

        response = self.client.chat.completions.create(
            model="meta-llama/llama-3-8b-instruct",
            messages=[
                {"role": "system", "content": "You are a professional planner. Always return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content.strip()

        # Remove markdown wrapping if present
        if content.startswith("```"):
            content = content.split("```")[1]

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            raise ValueError("LLM did not return valid JSON")