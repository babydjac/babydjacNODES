import requests

class FluxLifestylePromptNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "api_key": ("STRING", {"default": ""}),
            }
        }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("enhanced_prompt",)
    FUNCTION = "generate_prompt"
    CATEGORY = "babydjacNODES/Prompting/Flux"
    NODE_NAME = "FluxLifestylePromptNode"
    OUTPUT_NODE = True

    def generate_prompt(self, prompt, api_key):
        if not api_key:
            return ("Error: API key required.",)
        system_instruction = (
            "You are an expert prompt engineer for Flux/FAL image generation models. "
            "Given a user prompt, enhance and rewrite it into a concise, vivid, balanced lifestyle photograph prompt optimized for Flux Pro and Flux Pro 1.1. "
            "Include location, model overview, expression, pose, angle, placement, lighting, color palette, and styling with equal detail. "
            "Output ONLY the prompt text with no labels, explanations, or extra formatting."
        )
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "grok-3-latest",
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt.strip()}
            ],
            "temperature": 0.7,
            "stream": False,
        }
        try:
            response = requests.post("https://api.x.ai/v1/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return (content.strip(),)
        except Exception as e:
            return (f"API call failed: {e}",)

NODE_CLASS_MAPPINGS = {
    "FluxLifestylePromptNode": FluxLifestylePromptNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FluxLifestylePromptNode": "Flux Lifestyle Prompt Node",
}
