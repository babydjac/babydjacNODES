import json
import os
from typing import Dict

from .SafeTagListPromptNode import SafeTagListPromptNode


TEMPLATES_FILE = os.path.join(os.path.dirname(__file__), "templates.json")


def _load_templates() -> Dict[str, str]:
    try:
        with open(TEMPLATES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Ensure string-to-string mapping
        return {str(k): str(v) for k, v in data.items()}
    except Exception:
        return {}


class TemplateDrivenTagListPromptNode(SafeTagListPromptNode):
    """
    Template-driven variant that loads taglist templates from templates.json
    residing next to this file. Provides a CHOICE for template selection, and
    also supports an inline custom template override.

    Falls back to environment variable XAI_API_KEY if api_key input is empty.
    """

    @classmethod
    def INPUT_TYPES(cls):
        templates = _load_templates()
        names = sorted(list(templates.keys())) or ["<no-templates-found>"]
        base = super().INPUT_TYPES()
        # Build a fresh dict to avoid mutating base class config
        required = {
            "template_name": ("CHOICE", {"choices": names, "default": names[0]}),
            "custom_template": ("STRING", {"default": "", "multiline": True}),
            "custom_idea": ("STRING", {"default": "", "multiline": True}),
            "api_key": ("STRING", {"default": ""}),
        }
        optional = {
            "model_name": ("STRING", {"default": "grok-3-latest"}),
            "temperature": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.05}),
            "safe_mode": ("BOOLEAN", {"default": True}),
            "blocklist": ("STRING", {"default": base["optional"]["blocklist"][1]["default"], "multiline": True}),
        }
        return {"required": required, "optional": optional}

    FUNCTION = "process"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("taglist_prompt",)
    CATEGORY = "babydjacNODES/Taglists"
    NODE_NAME = "TemplateDrivenTagListPromptNode"
    OUTPUT_NODE = True

    def process(
        self,
        template_name,
        custom_template,
        custom_idea,
        api_key,
        model_name="grok-3-latest",
        temperature=0.2,
        safe_mode=True,
        blocklist="",
    ):
        templates = _load_templates()

        template_text = (custom_template or "").strip()
        if not template_text:
            template_text = templates.get(template_name, "").strip()

        if not template_text:
            return ("No template available. Provide 'custom_template' or add entries to templates.json.",)

        # Fallback to env var if no api_key provided
        resolved_key = api_key or os.environ.get("XAI_API_KEY", "")

        return super().process(
            template_text=template_text,
            custom_idea=custom_idea,
            api_key=resolved_key,
            model_name=model_name,
            temperature=temperature,
            safe_mode=safe_mode,
            blocklist=blocklist,
        )

NODE_CLASS_MAPPINGS = {
    "TemplateDrivenTagListPromptNode": TemplateDrivenTagListPromptNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TemplateDrivenTagListPromptNode": "Template Driven Taglist",
}
