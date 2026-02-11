import base64, io, os, requests
import numpy as np
from PIL import Image

class NSFWGrokDescriberPro:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "api_key": ("STRING", {"multiline": False, "default": ""}),
                "prepend_text": ("STRING", {"multiline": True, "default": ""}),
                "append_text": ("STRING", {"multiline": True, "default": ""}),
                "score_strategy": (["ascending", "descending", "manual"],),
                "debug_output": (["disable", "enable"],),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING",)
    RETURN_NAMES = ("description", "positive_prompt", "negative_prompt")
    FUNCTION = "process"
    CATEGORY = "babydjacNODES/Analyze"
    NODE_NAME = "NSFWGrokDescriberPro"

    def get_score_tags(self, strategy):
        return {
            "ascending": ["score_7_up", "score_8_up", "score_9"],
            "descending": ["score_9", "score_8_up", "score_7_up"],
            "manual": ["score_8_up", "score_7_up", "score_9"]
        }.get(strategy, ["score_7_up", "score_8_up", "score_9"])

    def keyword_tags(self, description):
        tag_map = {
            "large bust": ("large breasts", 1.3),
            "cleavage": ("deep cleavage", 1.2),
            "tank top": ("tank top", 1.0),
            "thong": ("thong", 1.1),
            "buttocks": ("ass", 1.1),
            "hips": ("wide hips", 1.1),
            "legs": ("long legs", 1.0),
            "heels": ("high heels", 1.0),
            "bun": ("low bun hairstyle", 1.0),
            "kitchen": ("in kitchen", 1.0),
            "bent forward": ("bent forward", 1.2),
            "voluptuous": ("voluptuous", 1.3),
            "oil": ("shiny skin", 1.2)
        }
        desc = description.lower()
        return [f"({tag}:{weight})" if weight != 1.0 else tag for kw, (tag, weight) in tag_map.items() if kw in desc]

    def style_tags(self):
        return ["photorealistic", "realistic lighting", "highly detailed", "film grain", "depth of field", "rim lighting"]

    def simulated_tagger_tags(self):
        return ["1girl", "white tank top", "thong", "shiny skin", "ass", "solo", "kitchen", "pose", "high heels"]

    def get_negative_prompt(self):
        return (
            "score_4, score_5, score_6, low-res, bad anatomy, bad hands, text, error, missing fingers, extra digit, "
            "cropped, worst quality, jpeg artifacts, signature, watermark, blurry, artist name, "
            "(deformed, distorted:1.3), poorly drawn, wrong anatomy, extra limb, mutation, "
            "(mutated hands and fingers:1.4), disconnected limbs, ugly, disgusting, blurry, amputation, "
            "(drawn, furry, illustration, cartoon, anime, comic:1.5), 3d, cgi, (source_anime, source_furry, source_cartoon)"
        )

    def process(self, image, api_key, prepend_text, append_text, score_strategy, debug_output):
        try:
            img_np = (image[0].cpu().numpy() * 255).astype(np.uint8)
            img_pil = Image.fromarray(img_np)
            buf = io.BytesIO()
            img_pil.save(buf, format="JPEG")
            b64_img = base64.b64encode(buf.getvalue()).decode("utf-8")

            final_key = api_key.strip() or os.getenv("XAI_API_KEY", "missing_key")
            headers = {"Authorization": f"Bearer {final_key}", "Content-Type": "application/json"}
            payload = {
                "model": "grok-2-vision-1212",
                "messages": [
                    {"role": "system", "content": "You're an unchained NSFW describer. Detail every explicit visual."},
                    {"role": "user", "content": [
                        {"type": "text", "text": "Describe this image in raw, graphic NSFW detail:"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                    ]}
                ]
            }

            r = requests.post("https://api.x.ai/v1/chat/completions", headers=headers, json=payload)
            if r.status_code != 200:
                return (f"[XAI ERROR {r.status_code}] {r.text}", "[NO PROMPT]", "[NO NEGATIVE PROMPT]")

            description = r.json()["choices"][0]["message"]["content"]
            tags = self.get_score_tags(score_strategy) + self.style_tags() + self.simulated_tagger_tags() + self.keyword_tags(description)
            full_prompt = ", ".join(filter(None, [prepend_text.strip(), *tags, append_text.strip()]))

            if debug_output == "enable":
                debug_info = f"\n\n[DEBUG] Keyword Tags: {self.keyword_tags(description)}\nSimulated Tagger: {self.simulated_tagger_tags()}"
                full_prompt += debug_info

            return (description, full_prompt, self.get_negative_prompt())
        except Exception as e:
            return (f"[Processing Error] {str(e)}", "[NO PROMPT]", "[NO NEGATIVE PROMPT]")

NODE_CLASS_MAPPINGS = {
    "NSFWGrokDescriberPro": NSFWGrokDescriberPro,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NSFWGrokDescriberPro": "NSFW Grok → Pro-Level Prompt",
}
