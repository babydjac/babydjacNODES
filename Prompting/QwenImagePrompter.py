from __future__ import annotations

import re
from typing import Dict, Tuple

import requests


QWEN_PROMPT_GUIDE = (
    "You are an expert prompt writer for Qwen-Image (image generation). "
    "Write a single, concise prompt optimized for Qwen-Image following these rules: "
    "1) Keep it 1–3 sentences in plain English. "
    "2) Order: main subject first, then visual style/medium, then environment & background; optionally mood/lighting and composition if relevant. "
    "3) If the user needs text rendered in the image, include the exact words in double quotes. "
    "4) Do NOT include parameters (steps, guidance/cfg, seed) in the text. "
    "5) No labels, headers, or Markdown; output the prompt only."
)


class QwenImagePrompter:
    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Dict[str, Tuple[str, Dict[str, object]]]]:
        return {
            "required": {
                "idea": ("STRING", {"default": "", "multiline": True}),
                "api_key": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("qwen_prompt",)
    FUNCTION = "generate_prompt"
    CATEGORY = "babydjacNODES/Prompting"
    NODE_NAME = "QwenImagePrompter"
    OUTPUT_NODE = True

    def _clean_output(self, text: str) -> str:
        # Remove common bold/label prefixes if any model adds them
        text = re.sub(r"^\s*\*\*[^\n]+\*\*:?\s*", "", text.strip())
        # Strip trailing quotes/period artifacts
        return text.strip().strip("\n").strip()

    def generate_prompt(self, idea: str, api_key: str) -> Tuple[str]:
        idea = (idea or "").strip()
        if not api_key:
            return ("Error: API key required.",)
        if not idea:
            return ("Please provide a short description of your image idea.",)

        messages = [
            {"role": "system", "content": QWEN_PROMPT_GUIDE},
            {"role": "user", "content": idea},
        ]

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": "grok-3-latest",
            "messages": messages,
            "temperature": 0.3,
            "stream": False,
        }

        try:
            resp = requests.post(
                "https://api.x.ai/v1/chat/completions", json=data, headers=headers, timeout=30
            )
            resp.raise_for_status()
            payload = resp.json()
            choices = payload.get("choices") or []
            content = (
                (choices[0].get("message") or {}).get("content") if choices else ""
            )
            if not content:
                return ("No output returned. Try refining your idea.",)
            cleaned = self._clean_output(content)
            return (cleaned,)
        except requests.exceptions.Timeout:
            return ("API call timed out. Please try again.",)
        except requests.exceptions.RequestException as e:
            return (f"API call failed: {e}",)
        except ValueError:
            return ("Invalid response from API.",)

NODE_CLASS_MAPPINGS = {
    "QwenImagePrompter": QwenImagePrompter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "QwenImagePrompter": "Qwen Image Prompter",
}
