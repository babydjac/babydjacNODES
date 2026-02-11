class DynamicPromptBatcher:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt_1": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompts",)
    FUNCTION = "collect"
    CATEGORY = "babydjacNODES/Utils/Batching"
    OUTPUT_IS_LIST = (True,)

    def collect(self, **kwargs):
        prompts = []
        for key in sorted(kwargs.keys()):
            val = kwargs[key]
            if isinstance(val, str) and val.strip():
                prompts.append(val.strip())
        return (prompts,)


NODE_CLASS_MAPPINGS = {
    "DynamicPromptBatcher": DynamicPromptBatcher,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DynamicPromptBatcher": "Prompt Rotator (Dynamic Batch)",
}
