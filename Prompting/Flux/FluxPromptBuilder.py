import os
import time
from typing import Optional


class FluxPromptBuilder:
    CATEGORY = "babydjacNODES/Prompting/Flux"
    NODE_NAME = "FluxPromptBuilder"
    WEB_DIRECTORY = "flux_prompt_suite"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("positive", "negative")
    FUNCTION = "generate"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "subject": ("STRING", {"default": "vague subject (e.g., portrait in studio)"}),
                "style": ([
                    "cinematic",
                    "glamour",
                    "artistic nude",
                    "editorial",
                    "film still",
                    "photoreal",
                    "analog",
                ], {}),
                "camera": ([
                    "35mm",
                    "50mm",
                    "85mm",
                    "macro",
                    "telephoto",
                ], {}),
                "lighting": ([
                    "softbox",
                    "rembrandt",
                    "split",
                    "rim",
                    "golden hour",
                    "hdr studio",
                ], {}),
                "spice": ("FLOAT", {"default": 0.35, "min": 0.0, "max": 1.0, "step": 0.01}),
                "safety_level": (["cautious", "standard", "raw"], {}),
                "use_grok": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "grok_api_key": ("STRING", {"default": "", "multiline": False, "placeholder": "sk-..."}),
                "guidance_tags": ("STRING", {"default": ""}),
                "forbidden_tags": ("STRING", {"default": "lowres, blurry, watermark"}),
                "prompt_override": ("STRING", {"default": ""}),
                "use_canvas_ui": ("BOOLEAN", {"default": False}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "prompt": "PROMPT",
            },
        }

    @classmethod
    def VALIDATE_INPUTS(cls, input_types=None, **consts):
        spice = consts.get("spice", 0.35)
        if not (0.0 <= float(spice) <= 1.0):
            return "spice must be in [0.0, 1.0]"
        return True

    @classmethod
    def IS_CHANGED(cls, *args, **kwargs):
        # Rerun on any widget change and occasionally if using external API
        key = (
            kwargs.get("subject"),
            kwargs.get("style"),
            kwargs.get("camera"),
            kwargs.get("lighting"),
            float(kwargs.get("spice", 0.0)),
            kwargs.get("safety_level"),
            bool(kwargs.get("use_grok", False)),
            kwargs.get("guidance_tags"),
            kwargs.get("forbidden_tags"),
            bool(kwargs.get("prompt_override")),
        )
        return key

    # --- Helper builders -------------------------------------------------
    def _build_system_prompt(self, safety_level: str) -> str:
        # Keep system prompt neutral; do not inject explicit content
        base = (
            "You are a senior prompt engineer for the Stability AI Flux model. "
            "Generate a compact, production-grade positive text prompt that emphasizes composition, camera, and lighting. "
            "Avoid verbose prose and avoid explicit sexual descriptions. Use tasteful, aesthetic descriptors only. "
            "Output only the positive prompt without quotes."
        )
        if safety_level == "cautious":
            base += " Maintain PG-13 wording and exclude any explicit terms."
        elif safety_level == "standard":
            base += " Keep professional tone and tasteful vocabulary."
        else:  # raw
            base += " Keep concise and aesthetic; no explicit terms."
        return base

    def _template_positive(self, subject: str, style: str, camera: str, lighting: str, spice: float, guidance: str) -> str:
        # Deterministic template with style knobs
        accents = []
        if spice >= 0.15:
            accents.append("shallow depth of field" if camera in ("85mm", "telephoto") else "cinematic composition")
        if spice >= 0.35:
            accents.append("skin-tone fidelity, natural gradients")
        if spice >= 0.6:
            accents.append("fine texture detail, micro-contrast")
        if spice >= 0.8:
            accents.append("film grain subtle, analog bloom")

        parts = [
            subject.strip(),
            f"style: {style}",
            f"camera: {camera}",
            f"lighting: {lighting}",
        ]
        if guidance.strip():
            parts.append(f"tags: {guidance.strip()}")
        if accents:
            parts.append("; ".join(accents))
        # Flux tends to like concise, comma-separated fragments
        return ", ".join([p for p in parts if p])

    def _template_negative(self, safety_level: str, forbidden: str) -> str:
        base_neg = [
            "lowres", "jpeg artifacts", "blurry", "overexposed", "underexposed", "posterization",
            "disfigured", "deformed", "poor anatomy", "bad hands", "extra limbs", "mutated",
        ]
        if safety_level == "cautious":
            base_neg += ["nudity", "explicit", "sexual content", "suggestive"]
        elif safety_level == "standard":
            base_neg += ["explicit", "sexual content"]
        # raw: do not add extra NSFW blocks here (still avoid explicit strings in code)
        if forbidden.strip():
            base_neg += [t.strip() for t in forbidden.split(",") if t.strip()]
        # Deduplicate
        seen = set()
        out = []
        for t in base_neg:
            if t not in seen:
                seen.add(t)
                out.append(t)
        return ", ".join(out)

    # --- Main ------------------------------------------------------------
    def generate(
        self,
        subject: str,
        style: str,
        camera: str,
        lighting: str,
        spice: float,
        safety_level: str,
        use_grok: bool,
        guidance_tags: Optional[str] = "",
        forbidden_tags: Optional[str] = "",
        prompt_override: Optional[str] = "",
        unique_id: Optional[str] = None,
        prompt: Optional[dict] = None,
    ):
        # If UI provided a final override, prefer it
        if prompt_override and prompt_override.strip():
            positive = prompt_override.strip()
        else:
            # Deterministic local template
            positive = self._template_positive(subject, style, camera, lighting, float(spice), guidance_tags or "")
            # Note: A separate aiohttp route can upgrade this via Grok and the JS UI can write back via hidden widget.

        negative = self._template_negative(safety_level, forbidden_tags or "")

        # Attach small provenance hints into EXTRA_PNGINFO via downstream saver if desired.
        return (positive, negative)

NODE_CLASS_MAPPINGS = {
    "FluxPromptBuilder": FluxPromptBuilder,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FluxPromptBuilder": "Flux Prompt Builder",
}
