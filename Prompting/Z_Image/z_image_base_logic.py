import base64
import json
import re
from io import BytesIO
from typing import Dict, Tuple

import numpy as np
from PIL import Image
import requests


SYSTEM_PROMPT = """
You are a senior prompt engineer for Z-Image Base (undistilled). Your job is to
create a high-quality, model-ready prompt that captures the user's intent while
staying specific, grounded, and visually concrete. Z-Image Base supports CFG and
negative prompts.

Output rules (strict):
- Return ONLY a JSON object with keys: prompt, negative_prompt, cfg, steps, breakdown.
- The prompt must be a single paragraph (no lists, no labels, no sections).
- Avoid rigid templates. Vary ordering and phrasing based on the concept.
- Use concrete visual details (subject, setting, lighting, materials, mood, camera).
- If humans appear, explicitly state they are adults and describe clothing/coverage
  unless the user asks for something different.
- If text must appear in the image, include the exact text in English quotes and
  describe placement/typography.
- Avoid meta tags like "8k", "masterpiece", "best quality", "trending".

Negative prompt rules:
- Keep it concise and defect-focused (20–80 words).
- Include only likely failures or explicit avoid items; no massive laundry lists.
- Do not include user-requested text or desired elements.

Parameter rules:
- Use cfg between 3.0 and 5.0, steps between 40 and 50.
- If user asks for max quality, favor 50 steps and cfg 3.0–4.0.
- If user asks for speed, allow 35–40 steps and cfg 4.0–5.0.
""".strip()


class ZImageBasePromptLogic:
    STYLES: Dict[str, str] = {
        "None": "",
        "Photorealistic": "photorealistic rendering, natural textures, realistic materials",
        "Cinematic": "cinematic staging, dramatic visual language, filmic realism",
        "Documentary": "documentary realism, candid details, truthful color",
        "Fashion editorial": "editorial fashion styling, refined polish, studio sophistication",
        "Fine art portrait": "fine art portrait sensibility, gallery-grade finish",
        "Architectural": "architectural precision, clean geometry, controlled perspective",
        "Product photography": "premium product photography, precise highlights, clean reflections",
        "Macro realism": "macro realism, high micro-detail, tactile surfaces",
        "Illustrative realism": "illustrative realism, painterly precision, grounded lighting",
        "Oil painting": "oil painting texture, visible brushwork, classic pigment depth",
        "Watercolor": "watercolor wash, soft edges, translucent pigment",
        "3D render": "high-end 3D render, clean shading, realistic materials",
        "Film still": "film still aesthetic, subtle grain, cinematic exposure",
        "Vintage analog": "vintage analog character, gentle grain, nostalgic tone",
        "Minimalist design": "minimalist design, restrained elements, calm composition",
        "High contrast": "high-contrast aesthetic, bold tonal separation",
    }

    CAMERAS: Dict[str, str] = {
        "None": "",
        "Canon EOS R5": "Canon EOS R5 capture, refined color science",
        "Sony A1": "Sony A1 sensor clarity, ultra-sharp detail",
        "Nikon Z9": "Nikon Z9 full-frame dynamics, crisp highlights",
        "Fujifilm GFX100 II": "medium format GFX100 II, expansive dynamic range",
        "Leica SL2": "Leica SL2 character, subtle micro-contrast",
        "35mm film look": "35mm film look, organic grain, gentle rolloff",
        "85mm f/1.4 lens": "85mm f/1.4 portrait lens, shallow depth and creamy bokeh",
        "24mm wide angle": "24mm wide angle, immersive perspective, strong spatial depth",
        "50mm standard lens": "50mm standard perspective, natural proportions",
        "Tilt-shift": "tilt-shift optics, precise focus plane, architectural control",
    }

    LIGHTING: Dict[str, str] = {
        "None": "",
        "Soft window light": "soft window light, gentle wrap, subtle shadows",
        "Golden hour": "golden hour warmth, low sun, glowing highlights",
        "Overcast": "overcast diffusion, shadowless softness, even tone",
        "Studio softbox": "studio softbox key light, controlled speculars",
        "Rim light": "rim light separation, defined edge highlights",
        "Noir hard light": "noir hard light, sharp shadow edges, moody contrast",
        "Cinematic top light": "cinematic top light, sculpted forms, dramatic depth",
        "Neon practicals": "neon practical lighting, saturated edge glow",
        "Candlelight": "candlelight warmth, soft falloff, intimate mood",
    }

    FRAMING: Dict[str, str] = {
        "None": "",
        "Close-up": "close-up framing, intimate detail emphasis",
        "Medium shot": "medium shot, balanced subject context",
        "Full body": "full-body framing, complete silhouette and posture",
        "Wide establishing": "wide establishing shot, environment-forward context",
        "Rule of thirds": "rule-of-thirds composition, deliberate balance",
        "Centered symmetry": "centered symmetry, formal visual balance",
        "Over-the-shoulder": "over-the-shoulder framing, narrative perspective",
        "Top-down": "top-down angle, graphic layout clarity",
        "Low angle": "low-angle view, elevated scale impression",
        "High angle": "high-angle view, observational perspective",
    }

    MOODS: Dict[str, str] = {
        "None": "",
        "Calm": "calm, composed mood",
        "Tense": "tense, charged atmosphere",
        "Hopeful": "hopeful, uplifting tone",
        "Melancholic": "melancholic, subdued tone",
        "Joyful": "joyful, bright energy",
        "Mysterious": "mysterious, ambiguous mood",
        "Luxurious": "luxurious, premium feel",
        "Gritty": "gritty, textured atmosphere",
        "Serene": "serene, quiet stillness",
    }

    PALETTES: Dict[str, str] = {
        "None": "",
        "Warm earth tones": "warm earth tones, natural browns and ambers",
        "Cool muted": "cool muted palette, restrained blues and grays",
        "Monochrome": "monochrome palette with subtle tonal shifts",
        "Vibrant pop": "vibrant pop colors, bold accents",
        "Desaturated": "desaturated palette, understated color",
        "High key": "high-key palette, bright airy tones",
        "Low key": "low-key palette, deep shadows and rich blacks",
    }

    DETAIL_FOCUS: Dict[str, str] = {
        "None": "",
        "Skin texture": "natural skin texture, visible pores, realistic translucency",
        "Material realism": "material realism, accurate surface roughness and speculars",
        "Architecture lines": "clean architectural lines, accurate perspective",
        "Depth of field": "controlled depth of field, intentional focus plane",
        "Micro detail": "micro-detail emphasis, fine textures, crisp edges",
        "Motion cues": "subtle motion cues, believable movement blur where needed",
    }

    NEGATIVE_PRESETS: Dict[str, str] = {
        "None": "",
        "Artifacts": "blurry, low detail, banding, color fringing, compression artifacts",
        "Anatomy": "bad anatomy, extra limbs, malformed hands, fused fingers",
        "Text/Watermark": "text, watermark, logo, brand marks",
        "Clutter": "busy background, cluttered scene, distracting elements",
        "All": "blurry, low detail, banding, color fringing, bad anatomy, extra limbs, malformed hands, text, watermark, logos, clutter",
    }

    LENGTH_GUIDE = {
        "Lean": "~80-120 words",
        "Standard": "~120-170 words",
        "Rich": "~170-230 words",
        "Ultra": "~220-280 words",
    }

    @staticmethod
    def _clean_text(text: str) -> str:
        return re.sub(r"\s+", " ", (text or "").strip())

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        words = text.split()
        return int(len(words) * 1.3) + 2

    @staticmethod
    def _process_image(image) -> str:
        if image is None:
            return ""
        img_tensor = image[0]
        arr = (img_tensor.clamp(0, 1) * 255.0).cpu().numpy().astype(np.uint8)
        img = Image.fromarray(arr)
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=95)
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{b64}"

    @classmethod
    def _build_context(
        cls,
        user_idea: str,
        prompt_length: str,
        style: str,
        camera: str,
        lighting: str,
        framing: str,
        mood: str,
        color_palette: str,
        detail_focus: str,
        negative_focus: str,
        quality_preset: str,
        must_include: str,
        avoid: str,
    ) -> str:
        parts = [f"USER CONCEPT: {user_idea}"]
        parts.append(f"TARGET LENGTH: {cls.LENGTH_GUIDE.get(prompt_length, 'Standard length')}")
        if must_include:
            parts.append(f"MUST INCLUDE: {must_include}")
        if avoid:
            parts.append(f"AVOID: {avoid}")
        if style != "None":
            parts.append(f"STYLE: {style} ({cls.STYLES.get(style, '')})")
        if camera != "None":
            parts.append(f"CAMERA: {camera} ({cls.CAMERAS.get(camera, '')})")
        if lighting != "None":
            parts.append(f"LIGHTING: {lighting} ({cls.LIGHTING.get(lighting, '')})")
        if framing != "None":
            parts.append(f"FRAMING: {framing} ({cls.FRAMING.get(framing, '')})")
        if mood != "None":
            parts.append(f"MOOD: {mood} ({cls.MOODS.get(mood, '')})")
        if color_palette != "None":
            parts.append(f"PALETTE: {color_palette} ({cls.PALETTES.get(color_palette, '')})")
        if detail_focus != "None":
            parts.append(f"DETAIL FOCUS: {detail_focus} ({cls.DETAIL_FOCUS.get(detail_focus, '')})")
        if negative_focus != "None":
            parts.append(f"NEGATIVE FOCUS: {negative_focus} ({cls.NEGATIVE_PRESETS.get(negative_focus, '')})")
        parts.append(f"QUALITY PRESET: {quality_preset}")
        return "\n".join(parts)

    @classmethod
    def _default_params(cls, quality_preset: str) -> Tuple[float, int]:
        if quality_preset == "Fast Draft":
            return 4.5, 38
        if quality_preset == "Max Quality":
            return 3.5, 50
        if quality_preset == "Exploration":
            return 3.0, 45
        return 4.0, 45

    @classmethod
    def _build_negative_prompt(cls, avoid: str, negative_focus: str) -> str:
        parts = []
        if negative_focus and negative_focus != "None":
            parts.append(cls.NEGATIVE_PRESETS.get(negative_focus, ""))
        if avoid:
            parts.append(avoid)
        cleaned = ", ".join([p.strip() for p in parts if p.strip()])
        return cls._clean_text(cleaned)

    @classmethod
    def generate_expert_prompt(
        cls,
        user_idea: str,
        prompt_length: str,
        style: str,
        camera: str,
        lighting: str,
        framing: str,
        mood: str,
        color_palette: str,
        detail_focus: str,
        negative_focus: str,
        quality_preset: str,
        must_include: str = "",
        avoid: str = "",
        api_key: str = "",
        grok_model: str = "grok-2-vision-1212",
        image_input=None,
    ):
        user_idea = cls._clean_text(user_idea)
        must_include = cls._clean_text(must_include)
        avoid = cls._clean_text(avoid)

        if api_key and api_key.strip():
            base64_img = cls._process_image(image_input)
            context = cls._build_context(
                user_idea,
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
                must_include,
                avoid,
            )

            user_content = [{"type": "text", "text": context}]
            if base64_img:
                user_content.append({
                    "type": "image_url",
                    "image_url": {"url": base64_img, "detail": "high"},
                })

            payload = {
                "model": grok_model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                "temperature": 0.65,
                "max_tokens": 1200,
                "stream": False,
            }

            headers = {
                "Authorization": f"Bearer {api_key.strip()}",
                "Content-Type": "application/json",
            }

            try:
                response = requests.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=40,
                )
                if response.status_code != 200:
                    err_msg = f"HTTP {response.status_code}: {response.text}"
                    return (
                        f"ERROR: {err_msg}",
                        cls._build_negative_prompt(avoid, negative_focus),
                        *cls._default_params(quality_preset),
                        "API Failed",
                        "See prompt output for details.",
                    )

                data = response.json()
                content = data["choices"][0]["message"]["content"].strip()

                try:
                    parsed = json.loads(content)
                    prompt = cls._clean_text(parsed.get("prompt", ""))
                    negative = cls._clean_text(parsed.get("negative_prompt", ""))
                    cfg = float(parsed.get("cfg", cls._default_params(quality_preset)[0]))
                    steps = int(parsed.get("steps", cls._default_params(quality_preset)[1]))
                    breakdown = parsed.get("breakdown", "Generated by Grok.")
                    status = f"Source: Grok API | ~{cls._estimate_tokens(prompt)} Toks"
                    return (prompt, negative, cfg, steps, status, breakdown)
                except Exception:
                    # Fallback if model returns plain text
                    prompt = cls._clean_text(content)
                    cfg, steps = cls._default_params(quality_preset)
                    status = f"Source: Grok API | ~{cls._estimate_tokens(prompt)} Toks"
                    breakdown = "Grok returned non-JSON; used raw prompt text."
                    return (prompt, cls._build_negative_prompt(avoid, negative_focus), cfg, steps, status, breakdown)

            except Exception as exc:
                return (
                    f"NETWORK ERROR: {exc}",
                    cls._build_negative_prompt(avoid, negative_focus),
                    *cls._default_params(quality_preset),
                    "Network Failed",
                    str(exc),
                )

        # Fallback: static logic
        core_prompt = user_idea or "a visually detailed subject"
        parts = [core_prompt]

        for value in (
            cls.FRAMING.get(framing, ""),
            cls.CAMERAS.get(camera, ""),
            cls.LIGHTING.get(lighting, ""),
            cls.MOODS.get(mood, ""),
            cls.PALETTES.get(color_palette, ""),
            cls.DETAIL_FOCUS.get(detail_focus, ""),
            cls.STYLES.get(style, ""),
        ):
            if value:
                parts.append(value)

        if must_include:
            parts.append(must_include)

        final_prompt = ", ".join([p for p in parts if p])
        cfg, steps = cls._default_params(quality_preset)
        negative = cls._build_negative_prompt(avoid, negative_focus)
        toks = cls._estimate_tokens(final_prompt)
        status = f"Source: Static Logic | ~{toks} Toks"
        breakdown = "Used static expansion (no API key)."

        return (final_prompt, negative, cfg, steps, status, breakdown)
