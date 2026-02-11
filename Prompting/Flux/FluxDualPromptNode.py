import requests
import json

class FluxDualPromptNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key":      ("STRING", {"default": "", "multiline": False}),
                "idea":         ("STRING", {"default": "A short description of the scene or concept", "multiline": True}),
                "model":        ("STRING", {"default": "grok-3-latest"}),
                "temperature":  ("FLOAT",  {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("STRING","STRING")
    FUNCTION = "generate_prompts"
    CATEGORY = "babydjacNODES/Prompting/Flux"
    NODE_NAME = "FluxDualPromptNode"

    def generate_prompts(self, api_key, idea, model, temperature):
        if not api_key:
            raise ValueError("API key is required")
        url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        system_msg = (
            "You are Grok, an expert prompt engineer for Flux 1D photorealistic images. "
            "Given a loose image idea, output a JSON object with two keys:\n"
            "1. \"clip_l\": a comma-separated list of concise keywords (max ~77 tokens) "
            "covering subject, style, camera & lighting cues.\n"
            "2. \"t5xxl\": a flowing multi-sentence scene description with foreground, "
            "mid-ground, background, and photorealism details."
        )
        user_msg = f"Image idea: {idea}"

        payload = {
            "model": model,
            "messages": [
                {"role": "system",  "content": system_msg},
                {"role": "user",    "content": user_msg}
            ],
            "temperature": temperature
        }

        resp = requests.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        out = resp.json()["choices"][0]["message"]["content"].strip()

        # Try parsing as JSON
        try:
            data = json.loads(out)
            clip_prompt = data.get("clip_l","").strip()
            t5_prompt   = data.get("t5xxl","").strip()
        except json.JSONDecodeError:
            # Fallback: split on "t5xxl"
            low = out.lower()
            if "t5xxl" in low:
                parts = out.split("t5xxl",1)
                clip_prompt = parts[0].split("clip_l",1)[-1].split(":",1)[-1].strip()
                t5_prompt   = parts[1].split(":",1)[-1].strip()
            else:
                raise ValueError("Could not parse Grok output into clip_l/t5xxl")

        return (clip_prompt, t5_prompt)

NODE_CLASS_MAPPINGS = {
    "FluxDualPromptNode": FluxDualPromptNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FluxDualPromptNode": "Flux Dual Prompt Node (Grok)",
}
