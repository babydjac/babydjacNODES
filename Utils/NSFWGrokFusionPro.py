import re

class NSFWGrokFusionPro:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_prompt": ("STRING", {"multiline": True, "default": ""}),
                "strategy": (["beginner", "balanced", "expert", "photorealism_max"], {"default": "balanced"}),
                "tag_weight": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 2.0, "step": 0.1}),
                "preset": (["None", "Softcore", "Hardcore Realism", "Cinematic", "Studio Lighting"], {"default": "None"}),
                "annotator": ("BOOLEAN", {"default": False}),
                "second_prompt": ("STRING", {"multiline": True, "default": ""}),
                "blend_weight": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.1}),
                "auto_cycle": ("BOOLEAN", {"default": False}),
                "cycle_styles": ("STRING", {"multiline": True, "default": ""}),
            },
            "optional": {
                "base_negative": ("STRING", {"multiline": True, "default": ""}),
            },
            "hidden": {"unique_id": "UNIQUE_ID"},
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING",)
    RETURN_NAMES = ("positive_prompt", "negative_prompt", "annotation",)
    FUNCTION = "generate"
    CATEGORY = "babydjacNODES/Utils"
    NODE_NAME = "NSFWGrokFusionPro"

    def generate(self, base_prompt, strategy, tag_weight, preset, annotator, second_prompt="", blend_weight=0.5, auto_cycle=False, cycle_styles="", base_negative="", unique_id=None):
        presets = {
            "Softcore": "soft lighting, sensual pose, score_7_up",
            "Hardcore Realism": "photorealistic, detailed anatomy, nsfw explicit, score_9",
            "Cinematic": "cinematic lighting, dramatic shadows, film grain",
            "Studio Lighting": "studio lighting, high key, professional photo",
        }

        positive = base_prompt
        if preset != "None":
            positive += ", " + presets.get(preset, "")

        strategies = {
            "beginner": "score_7_up, ",
            "balanced": "score_8_up, score_7_up, ",
            "expert": "score_9, score_8_up, ",
            "photorealism_max": "score_9, photorealistic, raw photo, 8k, ",
        }
        positive = strategies.get(strategy, "") + positive

        def scale_weights(prompt, scale):
            def repl(m):
                return f"({m.group(1)}:{float(m.group(2))*scale:.2f})"
            return re.sub(r'\(([^:]+):([\d.]+)\)', repl, prompt)

        positive = scale_weights(positive, tag_weight)

        if second_prompt:
            positive = f"({positive}:{1 - blend_weight}), ({second_prompt}:{blend_weight})"

        if auto_cycle and cycle_styles:
            styles = [s.strip() for s in cycle_styles.split(',')]
            variants = [positive + ", " + s for s in styles]
            positive = " | ".join(variants)  # Separator for variants

        negative = base_negative or "blurry, deformed, ugly, mutated, extra limbs, poor anatomy"
        negative += ", lowres, artifacts, jpeg artifacts, low quality"

        max_tokens = 75
        if len(positive.split(',')) > max_tokens:  # Approximate tokens by commas
            tags = positive.split(',')
            sorted_tags = sorted(tags, key=lambda x: float(re.search(r':([\d.]+)', x).group(1)) if ': ' in x else 1.0, reverse=True)
            positive = ','.join(sorted_tags[:max_tokens])

        score = f"Length: {len(positive.split(','))}, Realism tags: {positive.count('real')}, Style balance: {'good' if 20 < len(positive.split(',')) < 50 else 'adjust'}"

        annotation = ""
        if annotator:
            annotation = f"# Annotated Prompt Breakdown:\n# Base: {base_prompt}\n# Strategy: {strategies.get(strategy, '')}\n# Preset: {presets.get(preset, '')}\n# Scaled Weights: applied {tag_weight}\n# Blended: {bool(second_prompt)}\n# Variants: {len(styles) if auto_cycle else 0}\n# Score: {score}"

        return (positive, negative, annotation,)

NODE_CLASS_MAPPINGS = {
    "NSFWGrokFusionPro": NSFWGrokFusionPro
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NSFWGrokFusionPro": "Grok Prompt Fusion Pro"
}
