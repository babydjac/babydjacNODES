import re
import requests


DEFAULT_BLOCKLIST = [
    # Minimal NSFW/explicit keywords blocklist; extend as needed
    "nsfw", "porn", "sexual", "sex", "nude", "naked", "topless", "boobs",
    "breast", "areola", "pussy", "ass", "butt", "buttocks", "erotic",
    "explicit", "horny", "aroused", "arousing", "cum", "ejaculate", "semen",
    "oral", "anal", "penetration", "blowjob", "handjob", "vagina", "penis",
    "cock", "dick", "fetish", "bdsm"
]


class SafeTagListPromptNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "template_text": ("STRING", {"default": "", "multiline": True}),
                "custom_idea": ("STRING", {"default": "", "multiline": True}),
                "api_key": ("STRING", {"default": ""}),
            },
            "optional": {
                "model_name": ("STRING", {"default": "grok-3-latest"}),
                "temperature": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 1.0, "step": 0.05}),
                "safe_mode": ("BOOLEAN", {"default": True}),
                "blocklist": ("STRING", {"default": ", ".join(DEFAULT_BLOCKLIST), "multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("taglist_prompt",)
    FUNCTION = "process"
    CATEGORY = "babydjacNODES/Taglists"
    NODE_NAME = "SafeTagListPromptNode"
    OUTPUT_NODE = True

    def _has_blocked_terms(self, text: str, terms) -> bool:
        if not text:
            return False
        # Build a regex that matches whole words (case-insensitive)
        escaped = [re.escape(t.strip()) for t in terms if t.strip()]
        if not escaped:
            return False
        pattern = re.compile(r"\\b(" + "|".join(escaped) + r")\\b", re.IGNORECASE)
        return bool(pattern.search(text))

    def process(self, template_text, custom_idea, api_key, model_name="grok-3-latest", temperature=0.2, safe_mode=True, blocklist=", ".join(DEFAULT_BLOCKLIST)):
        template_text = (template_text or "").strip()
        custom_idea = (custom_idea or "").strip()

        if not api_key:
            return ("No API key provided.",)

        if not template_text:
            return ("Please provide a template taglist in 'template_text'.",)

        # Blocklist enforcement when safe_mode is on
        if safe_mode:
            terms = [t.strip() for t in (blocklist or "").split(",")]
            if self._has_blocked_terms(template_text, terms) or self._has_blocked_terms(custom_idea, terms):
                return ("Input rejected by safe_mode blocklist. Remove explicit terms and retry.",)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        system_prompt = (
            "You are an assistant that writes concise, comma-separated taglists for image prompts. "
            "Given a user idea and a template taglist, rewrite the user's idea as a single taglist that mirrors the structure, density, and style of the template. "
            "Keep content safe-for-work and non-explicit. Do not include sexual content or graphic anatomy. "
            f"Template taglist:\n{template_text}\n"
            "Output ONLY the new taglist, nothing else."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": custom_idea},
        ]

        data = {
            "model": model_name,
            "messages": messages,
            "stream": False,
            "temperature": float(temperature),
        }

        try:
            resp = requests.post("https://api.x.ai/v1/chat/completions", json=data, headers=headers, timeout=60)
            resp.raise_for_status()
            result = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")

            if not result:
                return ("No output returned. Try adjusting the template or inputs.",)

            # In safe_mode, do a quick post-check for blocked terms
            if safe_mode:
                terms = [t.strip() for t in (blocklist or "").split(",")]
                if self._has_blocked_terms(result, terms):
                    return ("Model output blocked by safe_mode. Try a different template/idea.",)

            return (result.strip(),)
        except requests.exceptions.RequestException as e:
            return (f"HTTP error contacting model API: {e}",)
        except Exception as e:
            return (f"Unexpected error: {e}",)

NODE_CLASS_MAPPINGS = {
    "SafeTagListPromptNode": SafeTagListPromptNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SafeTagListPromptNode": "Safe Tag List Prompt",
}
