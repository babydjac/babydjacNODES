import torch
from ...grok_model_catalog import ALL_GROK_MODELS
from .z_image_logic import ZImagePromptLogic

class ZImageTurboPromptEngineer:
    """
    A 'Studio' style prompt engineering node for Z-Image Turbo.
    Features massive customization, Grok Vision support, and expert breakdown analysis.
    """
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        # Matches WAN-Studio's model list EXACTLY
        GROK_MODELS = ALL_GROK_MODELS

        return {
            "required": {
                "text_input": ("STRING", {"multiline": True, "dynamicPrompts": True, "placeholder": "Enter your concept (e.g., 'cyberpunk street racer')..."}),
                
                # Z-Image Specific Controls
                "style": (list(ZImagePromptLogic.STYLES.keys()), {"default": "Photorealistic"}),
                "camera": (list(ZImagePromptLogic.CAMERAS.keys()), {"default": "None"}),
                "lighting": (list(ZImagePromptLogic.LIGHTING.keys()), {"default": "None"}),
                "framing": (list(ZImagePromptLogic.FRAMING.keys()), {"default": "None"}),
                
                # Inference Strategy
                "quality_preset": (["Speed", "Balanced", "Max Quality"], {"default": "Balanced"}),
            },
            "optional": {
                "grok_api_key": ("STRING", {"multiline": False, "placeholder": "xai-...", "default": ""}),
                "grok_model": (GROK_MODELS, {"default": "grok-2-vision-1212"}),
                "reference_image": ("IMAGE",), # Vision support!
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ("STRING", "FLOAT", "INT", "STRING", "STRING")
    RETURN_NAMES = ("optimized_prompt", "cfg", "steps", "status_info", "expert_breakdown")
    FUNCTION = "process"
    CATEGORY = "babydjacNODES/Prompting/Z-Image"
    NODE_NAME = "ZImageTurboPromptEngineer"
    WEB_DIRECTORY = "z_image_studio"

    def process(self, text_input, style, camera, lighting, framing, quality_preset, grok_api_key="", grok_model="grok-2-vision-1212", reference_image=None, unique_id=None, extra_pnginfo=None):
        
        final_prompt, cfg, steps, status, breakdown = ZImagePromptLogic.generate_expert_prompt(
            user_idea=text_input,
            style=style,
            camera=camera,
            lighting=lighting,
            framing=framing,
            quality_preset=quality_preset,
            api_key=grok_api_key,
            image_input=reference_image,
            grok_model=grok_model
        )

        return (final_prompt, cfg, steps, status, breakdown)

# Node Mapping
NODE_CLASS_MAPPINGS = {
    "ZImageTurboPromptEngineer": ZImageTurboPromptEngineer
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ZImageTurboPromptEngineer": "Z-Image Turbo Studio 🚀"
}
