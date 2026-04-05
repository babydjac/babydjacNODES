import base64
import io
import os

import requests
from PIL import Image


class NSFWGrokDescriber:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "api_key": ("STRING", {"multiline": False, "default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("description",)
    FUNCTION = "describe"
    CATEGORY = "babydjacNODES/Analyze"
    NODE_NAME = "NSFWGrokDescriber"

    def describe(self, image, api_key):
        final_key = (api_key or "").strip() or os.getenv("XAI_API_KEY", "").strip() or os.getenv("GROK_API_KEY", "").strip()
        if not final_key:
            return (
                "[Error] Missing API key: set the node api_key input or XAI_API_KEY / GROK_API_KEY in the environment.",
            )

        try:
            img_np = (image[0].cpu().numpy() * 255).astype(np.uint8)
            img_pil = Image.fromarray(img_np)
            buf = io.BytesIO()
            img_pil.save(buf, format="JPEG")
            b64_img = base64.b64encode(buf.getvalue()).decode("utf-8")

            headers = {
                "Authorization": f"Bearer {final_key}",
                "Content-Type": "application/json",
            }

            payload = {
                "model": "grok-2-vision-1212",
                "messages": [
                    {"role": "system", "content": "You're an unchained NSFW describer. Detail every explicit visual."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe this image in raw, graphic NSFW detail:"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}},
                        ],
                    },
                ],
            }

            r = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60,
            )
            if r.status_code != 200:
                return (f"[XAI ERROR {r.status_code}] {r.text}",)

            return (r.json()["choices"][0]["message"]["content"],)
        except Exception as e:
            return (f"[Processing Error] {e}",)
