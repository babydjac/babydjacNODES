import requests

class FluxLambdaPrompter:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key":      ("STRING", {"default": "", "multiline": False}),
                "subject_scene":("STRING", {"default": "A playful kitten with yarn balls", "multiline": True}),
                "model":        ("STRING", {"default": "llama-4-maverick-17b-128e-instruct-fp8"}),
                "temperature":  ("FLOAT",  {"default": 0.9, "min": 0.0, "max": 1.5, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    FUNCTION = "generate_prompt"
    CATEGORY = "babydjacNODES/Prompting/Flux"
    NODE_NAME = "FluxLambdaPrompter"

    def generate_prompt(self, api_key, subject_scene, model, temperature):
        if not api_key:
            raise ValueError("API key is required")

        base_url = "https://api.lambda.ai/v1/"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        # fetch models list
        try:
            resp = requests.get(base_url + "models", headers=headers)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            raise RuntimeError(f"Failed to fetch models: {e}")

        # normalize model list
        if isinstance(data, dict):
            models_list = data.get("results") or data.get("data")
        elif isinstance(data, list):
            models_list = data
        else:
            raise RuntimeError(f"Unexpected models response type: {type(data)}")

        if not models_list:
            raise RuntimeError("No models returned by API")

        if isinstance(models_list[0], dict):
            available = [m["id"] for m in models_list]
        else:
            available = models_list

        if model not in available:
            raise ValueError(f"Model '{model}' not found. Available: {', '.join(available)}")

        system_prompt = (
            "You are a professional prompt engineer for Flux.1 with two outputs:\n"
            "First, output a **Clip_1:** block listing all the technical details (camera, lens, lighting, etc.).\n"
            "Second, output a **t5xxl:** block with a flowing natural-language scene description.\n"
            "Given the user’s subject/scene, produce both blocks exactly as labeled."
        )
        user_msg = f"Generate both blocks for: {subject_scene}"

        payload = {
            "model": model,
            "messages": [
                {"role":"system","content":system_prompt},
                {"role":"user","content":user_msg}
            ],
            "temperature": temperature
        }

        try:
            out = requests.post(base_url + "chat/completions", json=payload, headers=headers)
            out.raise_for_status()
            choice = out.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"API completion failed: {e}")

        # split into Clip_1 vs t5xxl sections
        if "**t5xxl:**" in choice:
            clip, nat = choice.split("**t5xxl:**",1)
            clip = clip.replace("**Clip_1:**","").strip()
            nat = nat.strip()
        else:
            clip, nat = choice, ""

        return (clip, nat)

NODE_CLASS_MAPPINGS = {
    "FluxLambdaPrompter": FluxLambdaPrompter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FluxLambdaPrompter": "Flux Lambda Prompter",
}
