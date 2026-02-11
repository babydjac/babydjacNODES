import requests
import json

class NSFWGrokToPonyXL:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "description": ("STRING", {"default": "", "multiline": True}),
                "api_key": ("STRING", {"default": ""}),
                "motion_type": ("STRING", {"default": "hair swaying slightly"}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("ponyxl_prompt", "wan_prompt", "negative_prompt")
    FUNCTION = "generate_prompts"
    CATEGORY = "babydjacNODES/Prompting/PonyXL"
    NODE_NAME = "NSFWGrokToPonyXL"
    OUTPUT_NODE = True

    def generate_prompts(self, description, api_key, motion_type):
        if not api_key:
            return (description, "", "blurry, low_quality, bad_anatomy, oversaturated")
        try:
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
            data = {
                "messages": [
                    {
                        "role": "system",
                        "content": f"You are an expert in crafting detailed prompts for PonyXL and Wan video generation. For PonyXL, create a detailed prompt with essential and descriptive Danbooru tags (e.g., blonde_hair, gigantic_breasts, indoor_bedroom, detailed_background, intricate_clothing, dynamic_pose), comma-separated, including score_9, score_8_up, score_7_up, source_realistic, rating_mature, and avoiding vague descriptors like 'ultra_detailed'. For Wan, create a short video prompt starting with 'a video of' with the subject, their primary action, and a user-defined visual motion ('{motion_type}'). Also, provide a negative prompt for PonyXL (e.g., blurry, low_quality, bad_anatomy, oversaturated). Provide a brief explanation of the optimization. Return a JSON object with 'ponyxl_prompt', 'wan_prompt', 'negative_prompt', and 'explanation' keys."
                    },
                    {
                        "role": "user",
                        "content": f"Generate a detailed PonyXL prompt, a Wan video prompt, and a negative prompt for: {description}"
                    }
                ],
                "model": "grok-3-latest",
                "stream": False,
                "temperature": 0
            }
            response = requests.post("https://api.x.ai/v1/chat/completions", json=data, headers=headers)
            response.raise_for_status()
            result = response.json().get("choices", [{}])[0].get("message", {}).get("content", "{}")
            result_dict = json.loads(result)
            ponyxl_prompt = result_dict.get("ponyxl_prompt", description)
            wan_prompt = result_dict.get("wan_prompt", "")
            negative_prompt = result_dict.get("negative_prompt", "blurry, low_quality, bad_anatomy, oversaturated")
            return (ponyxl_prompt, wan_prompt, negative_prompt)
        except Exception as e:
            return (description, "", "blurry, low_quality, bad_anatomy, oversaturated")

NODE_CLASS_MAPPINGS = {
    "NSFWGrokToPonyXL": NSFWGrokToPonyXL,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NSFWGrokToPonyXL": "Grok to PonyXL Prompt",
}
