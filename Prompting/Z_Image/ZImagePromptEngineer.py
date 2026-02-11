from ...grok_model_catalog import ALL_GROK_MODELS
from .z_image_base_logic import ZImageBasePromptLogic


class ZImagePromptEngineer:
    """
    Advanced prompt engineering node for Z-Image Base (undistilled).
    Uses Grok when available, with a non-template prompt generation strategy.
    """

    @classmethod
    def INPUT_TYPES(cls):
        grok_models = ALL_GROK_MODELS

        return {
            "required": {
                "text_input": (
                    "STRING",
                    {
                        "multiline": True,
                        "dynamicPrompts": True,
                        "placeholder": "Describe the concept (e.g., 'storm-lit alpine cabin at dawn')...",
                    },
                ),
                "prompt_length": (
                    ["Lean", "Standard", "Rich", "Ultra"],
                    {"default": "Standard"},
                ),
                "style": (list(ZImageBasePromptLogic.STYLES.keys()), {"default": "Photorealistic"}),
                "camera": (list(ZImageBasePromptLogic.CAMERAS.keys()), {"default": "None"}),
                "lighting": (list(ZImageBasePromptLogic.LIGHTING.keys()), {"default": "None"}),
                "framing": (list(ZImageBasePromptLogic.FRAMING.keys()), {"default": "None"}),
                "mood": (list(ZImageBasePromptLogic.MOODS.keys()), {"default": "None"}),
                "color_palette": (list(ZImageBasePromptLogic.PALETTES.keys()), {"default": "None"}),
                "detail_focus": (list(ZImageBasePromptLogic.DETAIL_FOCUS.keys()), {"default": "None"}),
                "negative_focus": (
                    list(ZImageBasePromptLogic.NEGATIVE_PRESETS.keys()),
                    {"default": "Artifacts"},
                ),
                "quality_preset": (
                    ["Fast Draft", "Production", "Max Quality", "Exploration"],
                    {"default": "Production"},
                ),
            },
            "optional": {
                "must_include": (
                    "STRING",
                    {"multiline": True, "placeholder": "Hard requirements or specific details...", "default": ""},
                ),
                "avoid": (
                    "STRING",
                    {"multiline": True, "placeholder": "Things to avoid in the image...", "default": ""},
                ),
                "grok_api_key": (
                    "STRING",
                    {"multiline": False, "placeholder": "xai-...", "default": ""},
                ),
                "grok_model": (grok_models, {"default": "grok-2-vision-1212"}),
                "reference_image": ("IMAGE",),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "FLOAT", "INT", "STRING", "STRING")
    RETURN_NAMES = (
        "positive_prompt",
        "negative_prompt",
        "cfg",
        "steps",
        "status_info",
        "expert_breakdown",
    )
    FUNCTION = "process"
    CATEGORY = "babydjacNODES/Prompting/Z-Image"
    NODE_NAME = "ZImagePromptEngineer"
    WEB_DIRECTORY = "z_image_studio"

    def process(
        self,
        text_input,
        prompt_length,
        style,
        camera,
        lighting,
        framing,
        mood,
        color_palette,
        detail_focus,
        negative_focus,
        quality_preset,
        must_include="",
        avoid="",
        grok_api_key="",
        grok_model="grok-2-vision-1212",
        reference_image=None,
        unique_id=None,
        extra_pnginfo=None,
    ):
        prompt, negative, cfg, steps, status, breakdown = ZImageBasePromptLogic.generate_expert_prompt(
            user_idea=text_input,
            prompt_length=prompt_length,
            style=style,
            camera=camera,
            lighting=lighting,
            framing=framing,
            mood=mood,
            color_palette=color_palette,
            detail_focus=detail_focus,
            negative_focus=negative_focus,
            quality_preset=quality_preset,
            must_include=must_include,
            avoid=avoid,
            api_key=grok_api_key,
            grok_model=grok_model,
            image_input=reference_image,
        )

        return (prompt, negative, cfg, steps, status, breakdown)


NODE_CLASS_MAPPINGS = {
    "ZImagePromptEngineer": ZImagePromptEngineer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ZImagePromptEngineer": "Z-Image Base Studio ⚙️",
}
