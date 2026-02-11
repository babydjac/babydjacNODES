from __future__ import annotations

import base64
import io
import os
from typing import Any, Dict, Tuple

import requests
from PIL import Image
import random


def _to_pil_from_comfy(image: Any) -> Image.Image:
    try:
        import numpy as np  # noqa: F401
    except Exception:  # pragma: no cover - ComfyUI ships numpy
        raise

    # Support torch tensors or numpy arrays, shapes: [B,H,W,C] or [H,W,C], float 0-1 or uint8
    if hasattr(image, "detach") and callable(getattr(image, "detach", None)):
        arr = image.detach().cpu().numpy()
    elif hasattr(image, "cpu") and callable(getattr(image, "cpu", None)) and hasattr(image, "numpy"):
        arr = image.cpu().numpy()
    else:
        arr = image

    import numpy as np

    if isinstance(arr, list):
        arr = arr[0]
    arr = np.array(arr)
    if arr.ndim == 4:
        arr = arr[0]
    if arr.dtype != np.uint8:
        arr = (arr * 255.0).clip(0, 255).astype("uint8")
    if arr.shape[-1] == 1:
        arr = arr.squeeze(-1)
    img = Image.fromarray(arr)
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


def _pil_to_data_uri(img: Image.Image, fmt: str = "JPEG", quality: int = 90) -> str:
    buf = io.BytesIO()
    save_kwargs: Dict[str, Any] = {"format": fmt}
    if fmt.upper() == "JPEG":
        save_kwargs.update({"quality": quality, "optimize": True})
    img.save(buf, **save_kwargs)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    mime = "image/jpeg" if fmt.upper() == "JPEG" else f"image/{fmt.lower()}"
    return f"data:{mime};base64,{b64}"


def _normalize_tag(token: str) -> str:
    t = (token or "").strip().lower()
    # Replace spaces with underscores; drop leading/trailing punctuation
    t = t.replace(" ", "_")
    # Ban markdown bullets/hyphens and stray asterisks
    for ch in ["*", "-", "\n", "\r", "\t"]:
        t = t.replace(ch, "")
    # Collapse multiple underscores
    while "__" in t:
        t = t.replace("__", "_")
    return t.strip(",; ")


def _tags_from_analysis(text: str) -> list:
    # Prefer comma-separated list; if sentences, split heuristically.
    raw = (text or "").strip()
    if not raw:
        return []
    # If model returned bullets or JSON-like, replace separators with commas.
    seps = ["\n", "\r", ";", "|", " • ", "  "]
    for s in seps:
        raw = raw.replace(s, ", ")
    # Split on commas
    parts = [p for p in (x.strip() for x in raw.split(",")) if p]
    # Normalize to danbooru-like tokens
    tags = []
    for p in parts:
        # Strip any leading label like "subject:" or "- subject:"
        if ":" in p:
            _, val = p.split(":", 1)
            p = val
        tag = _normalize_tag(p)
        if tag:
            tags.append(tag)
    return tags


def _exaggeration_phrase(level: int) -> str:
    lvl = max(0, min(10, int(level)))
    if lvl <= 2:
        return "slightly enhanced breasts, subtle curves, toned butt"
    if lvl <= 4:
        return "noticeably full breasts, round butt, curvier hips"
    if lvl <= 6:
        return "prominent breasts, pronounced butt, hourglass figure"
    if lvl <= 8:
        return "large breasts, very curvy thick body, voluptuous butt"
    return "exaggerated oversized breasts, extremely curvy body, full round ass"


def _exaggeration_weights(level: int) -> list[str]:
    lvl = max(0, min(10, int(level)))
    # Map 0..10 to 1.0..1.5
    w = 1.0 + (0.5 * (lvl / 10.0))
    if w < 1.05:
        return []
    w_hips = max(1.0, w - 0.1)
    return [
        f"(exaggerated_breasts:{w:.1f})",
        f"(exaggerated_hips:{w_hips:.1f})",
        f"(exaggerated_ass:{w:.1f})",
    ]


def _compose_prompt_and_negative(
    analysis: str,
    exaggeration: int,
    add_realism_tags: bool,
    quality_boost: bool,
    custom_negatives: str,
    extra_tags: str,
) -> tuple[str, str]:
    prompt_tags = []
    negative_tags = []

    # Quality boosters
    if quality_boost:
        prompt_tags.extend([
            "score_9", "score_8_up", "score_7_up", "highly_detailed", "masterpiece", "best_quality",
        ])

    # Analysis as tags
    prompt_tags.extend(_tags_from_analysis(analysis))

    # Realism cluster
    if add_realism_tags:
        prompt_tags.extend([
            "photorealistic", "cinematic_lighting", "detailed_skin", "skin_texture", "realistic",
        ])

    # Exaggeration mapping → convert to tags
    ex_text = _exaggeration_phrase(exaggeration)
    prompt_tags.extend(_tags_from_analysis(ex_text))
    prompt_tags.extend(_exaggeration_weights(exaggeration))

    # Extra user-provided tags
    if extra_tags and extra_tags.strip():
        prompt_tags.extend(_tags_from_analysis(extra_tags))

    # Negatives separated; default avoids anime/cartoon styles
    negatives_default = "ugly, deformed, cartoon, anime, source_anime, source_pony, lowres, bad_anatomy, blurry, watermark"
    negatives_src = custom_negatives.strip() if custom_negatives and custom_negatives.strip() else negatives_default
    negative_tags.extend(_tags_from_analysis(negatives_src))

    # Deduplicate while preserving order
    def dedupe(seq):
        seen = set()
        out = []
        for t in seq:
            if t and t not in seen:
                seen.add(t)
                out.append(t)
        return out

    prompt_tags = dedupe(prompt_tags)
    negative_tags = dedupe(negative_tags)

    # Canonicalize to danbooru-style, enforce adult/21yo/nsfw heuristics, map vague terms
    prompt_tags = _canonicalize_prompt_tags(prompt_tags)
    negative_tags = _canonicalize_negative_tags(negative_tags)

    return ", ".join(prompt_tags), ", ".join(negative_tags)


def _call_grok_vision(
    api_key: str,
    base_url: str,
    data_uri: str,
    instruction: str,
    max_tokens: int,
    temperature: float,
    top_p: float = 1.0,
    frequency_penalty: float = 0.0,
    presence_penalty: float = 0.0,
    timeout: int = 60,
) -> str:
    url = base_url.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    sys_prompt = (
        "Return ONLY a single comma-separated line of lowercase danbooru-style tags. "
        "Use underscores, never spaces. No markdown, no bullets, no hyphens, no sentences. "
        "Subject count must use 1girl/2girls/1boy/2boys, never bare numbers. "
        "Age tag must be '21yo' (adult). If nude/explicit, include 'nsfw'. "
        "Prefer established tags (e.g., nude, large_breasts, huge_ass, hourglass_figure, lying_on_back, legs_spread, bedroom, white_bed, overhead_angle, cinematic_lighting). "
        "If a sexual act/position/fetish appears, include precise canonical tags. Examples: large_penis, erect_penis, penis_in_vagina, penis_in_mouth, penis_in_hand, penis_in_ass, doggystyle, cowgirl_position, reverse_cowgirl, missionary_position, anal_penetration, vaginal_penetration, deepthroat, blowjob, handjob, titfuck, paizuri, cunnilingus, rimming, fingering, fisting, double_penetration, creampie, cum_on_face, cum_on_body, cum_in_mouth, cum_inside, bukkake, gloryhole, spanking, hair_pulling, choking, bondage, collar_and_leash, group_sex, threesome, gangbang, public_sex, outdoor_sex, masturbation, female_ejaculation, squirting, nipple_clamps, bdsm, submission, dominance, rough_sex, passionate_kissing, spooning_position, standing_sex, wall_sex, table_sex, chair_sex, shower_sex, bathtub_sex, bed_sex, floor_sex, piledriver_position, mating_press, on_top. "
        "If subject is futa/shemale/dickgirl, include futa/futanari/shemale/dickgirl and explicit penis size/traits (e.g., huge_penis, thick_penis, big_balls) along with feminine traits (e.g., busty, large_breasts). "
        "Be creative and image-specific: include unique, accurate tags for hair color/style, eye color, accessories, textures, materials, environmental objects, composition (rule_of_thirds, leading_lines), camera/optics (depth_of_field, bokeh), time_of_day, and color_palette when visible. Avoid repeating the same generic set; adapt to the image. "
        "Avoid vague phrases; use canonical tags only."
    )
    user_text = instruction.strip() if instruction and instruction.strip() else (
        "Only tags, comma-separated: count (1girl/1boy/etc), age (21yo, adult), clothing, body_shape, pose, scene, camera, lighting."
    )
    body = {
        "model": "grok-2-vision-1212",
        "messages": [
            {"role": "system", "content": sys_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {"type": "image_url", "image_url": {"url": data_uri}},
                ],
            },
        ],
        "max_tokens": int(max_tokens),
        "temperature": float(temperature),
        "top_p": float(top_p),
        "frequency_penalty": float(frequency_penalty),
        "presence_penalty": float(presence_penalty),
        "stream": False,
    }

    resp = requests.post(url, json=body, headers=headers, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:  # pragma: no cover - depends on API
        raise RuntimeError(f"Unexpected Grok response format: {e}")


class GrokPonyXLPrompter:
    """ComfyUI node: Generate PonyXL-style prompt from an image via Grok Vision."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {}),
            },
            "optional": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "base_url": ("STRING", {"default": "https://api.x.ai/v1", "multiline": False}),
                "exaggeration": ("INT", {"default": 5, "min": 0, "max": 10, "step": 1}),
                "add_realism_tags": ("BOOLEAN", {"default": True}),
                "quality_boost": ("BOOLEAN", {"default": True}),
                "custom_negatives": ("STRING", {"default": "", "multiline": True}),
                "extra_tags": ("STRING", {"default": "", "multiline": True}),
                "instruction": ("STRING", {"default": "", "multiline": True}),
                "max_tokens": ("INT", {"default": 256, "min": 32, "max": 1024}),
                "temperature": ("FLOAT", {"default": 0.45, "min": 0.0, "max": 1.0, "step": 0.05}),
                "top_p": ("FLOAT", {"default": 0.9, "min": 0.1, "max": 1.0, "step": 0.05}),
                "frequency_penalty": ("FLOAT", {"default": 0.2, "min": 0.0, "max": 2.0, "step": 0.1}),
                "presence_penalty": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 2.0, "step": 0.1}),
                "shuffle_order": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "negative")
    FUNCTION = "generate"
    CATEGORY = "babydjacNODES/Prompting/PonyXL"
    NODE_NAME = "GrokPonyXLPrompter"

    def _resolve_api_key(self, explicit: str) -> str:
        key = (explicit or "").strip() or os.getenv("XAI_API_KEY", "").strip() or os.getenv("GROK_API_KEY", "").strip()
        if not key:
            raise ValueError("Missing API key: set 'api_key' or XAI_API_KEY/GROK_API_KEY env vars")
        return key

    def generate(
        self,
        image: Any,
        api_key: str = "",
        base_url: str = "https://api.x.ai/v1",
        exaggeration: int = 5,
        add_realism_tags: bool = True,
        quality_boost: bool = True,
        custom_negatives: str = "",
        extra_tags: str = "",
        instruction: str = "",
        max_tokens: int = 256,
        temperature: float = 0.45,
        top_p: float = 0.9,
        frequency_penalty: float = 0.2,
        presence_penalty: float = 0.0,
        shuffle_order: bool = True,
    ) -> Tuple[str, str]:
        key = self._resolve_api_key(api_key)

        # Encode image
        pil = _to_pil_from_comfy(image)
        data_uri = _pil_to_data_uri(pil, fmt="JPEG", quality=90)

        # Call Grok Vision
        analysis = _call_grok_vision(
            api_key=key,
            base_url=base_url,
            data_uri=data_uri,
            instruction=instruction,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        )

        # Compose final prompt and negatives (separate lines, danbooru-style)
        prompt, negative = _compose_prompt_and_negative(
            analysis=analysis,
            exaggeration=exaggeration,
            add_realism_tags=add_realism_tags,
            quality_boost=quality_boost,
            custom_negatives=custom_negatives,
            extra_tags=extra_tags,
        )
        # Optionally shuffle non-quality tags to encourage variety
        if shuffle_order and prompt:
            tags = [t.strip() for t in prompt.split(",") if t.strip()]
            quality_order = ["score_9", "score_8_up", "score_7_up", "highly_detailed", "masterpiece", "best_quality"]
            front = [t for t in tags if t in quality_order]
            rest = [t for t in tags if t not in quality_order]
            random.shuffle(rest)
            prompt = ", ".join(front + rest)

        return (prompt, negative)


def _canonicalize_prompt_tags(tags: list[str]) -> list[str]:
    # Detect presence for heuristics before dropping raw gender tokens
    lower_set = set(tags)
    has_male = any(t in lower_set for t in ("male", "man", "boy", "nude_male", "average_male"))
    has_female = any(t in lower_set for t in ("female", "woman", "girl", "1girl", "2girls"))

    synonyms = {
        "none": "nude",
        "no_clothes": "nude",
        "naked": "nude",
        "overhead_shot": "overhead_angle",
        "top_down": "overhead_angle",
        "soft_lighting": "soft_shadows",
        "natural_lighting": "natural_light",
        "pubic_area": "natural_pubic_hair",
        "natural_pubic_area": "natural_pubic_hair",
        "big_boobs": "large_breasts",
        "big_breasts": "large_breasts",
        "large_boobs": "large_breasts",
        "wide_hip": "wide_hips",
        "wide_hipss": "wide_hips",
        "legs_open": "legs_spread",
        "arms_resting_on_bed": "arms_at_sides",
        "overhead": "overhead_angle",
        # Vague phrases → canonical
        "extremely_curvy_body": "curvy",
        "super_curvy": "curvy",
        "full_round_ass": "huge_ass",
        "round_ass": "huge_ass",
        "exaggerated_oversized_breasts": "large_breasts",
        # Penis/cock synonyms & sizes
        "cock": "penis",
        "dick": "penis",
        "member": "penis",
        "shaft": "penis",
        "huge_cock": "huge_penis",
        "big_cock": "large_penis",
        "thick_cock": "thick_penis",
        "massive_cock": "huge_penis",
        "giant_cock": "huge_penis",
        "big_balls": "big_balls",
        # Futa synonyms
        "shemale": "shemale",
        "dickgirl": "dickgirl",
        "futa": "futa",
        "futanari": "futanari",
        # Sexual acts canonicalization (favor explicit tags per PonyXL usage)
        "piv": "penis_in_vagina",
        "vaginal": "penis_in_vagina",
        "vaginal_sex": "penis_in_vagina",
        "vaginal_penetration": "vaginal_penetration",
        "sex": "explicit",
        "anal": "anal_penetration",
        "anal_sex": "anal_penetration",
        "anal_intercourse": "anal_penetration",
        "doggy_style": "doggystyle",
        "doggy": "doggystyle",
        "from_behind": "doggystyle",
        "cowgirl": "cowgirl_position",
        "reverse_cowgirl_position": "reverse_cowgirl",
        "missionary": "missionary_position",
        "spooning": "spooning_position",
        "standing": "standing_sex",
        "wall": "wall_sex",
        "table": "table_sex",
        "chair": "chair_sex",
        "shower": "shower_sex",
        "bath": "bathtub_sex",
        "bathtub": "bathtub_sex",
        "bed": "bed_sex",
        "floor": "floor_sex",
        "piledriver": "piledriver_position",
        "suspended": "suspended_sex",
        "on_top_position": "on_top",
        "under_table": "under_table_sex",
        "fellatio": "blowjob",
        "bj": "blowjob",
        "boobjob": "titfuck",
        "titjob": "titfuck",
        "paizuri": "titfuck",
        "facial": "cum_on_face",
        "cum_on_the_face": "cum_on_face",
        "cum_inside": "cum_inside",
        "internal_ejaculation": "internal_ejaculation",
        "internal_cumshot": "cum_inside",
        "cream_pie": "creampie",
        "cumshot": "cum_shot",
        "cum_shot": "cum_shot",
        "semen": "cum",
        "ejaculation": "cum",
        "anilingus": "rimming",
        "facesitting": "face_sitting",
        "glory_hole": "gloryhole",
        "riding": "riding_cock",
        "reverse_cowgirl_riding": "reverse_cowgirl",
        "strap-on": "strap_on",
        "strapon": "strap_on",
        "toe_suck": "toe_sucking",
        "foot_fetishism": "foot_fetish",
        "public": "public_sex",
        "outdoor": "outdoor_sex",
        "licking_ass": "licking_anus",
        "pussy_eating": "cunnilingus",
        "pussy_licking": "cunnilingus",
        "pussy_lick": "cunnilingus",
        "snowball": "snowballing",
        "atm": "ass_to_mouth",
        "a2m": "ass_to_mouth",
        "double_pene": "double_penetration",
        "triple_pene": "triple_penetration",
        "breast_suck": "breast_sucking",
        "nipple_suck": "nipple_sucking",
        "nipple_play": "nipple_play",
        "nipple_clamp": "nipple_clamps",
        "collar_and_lead": "collar_and_leash",
        "leash": "collar_and_leash",
        "bdsm_play": "bdsm",
        "dominant": "dominance",
        "submissive": "submission",
    }

    def is_count_tag(t: str) -> bool:
        import re
        return re.match(r"^[0-9]+(girl|girls|boy|boys)$", t) is not None

    out: list[str] = []
    seen = set()
    added_nsfw = False
    has_nude = False
    has_explicit = False
    has_penis = False
    has_erect = False
    has_large = False
    has_blowjob = False
    has_handjob = False
    has_futa = False

    for raw in tags:
        t = raw
        if not t:
            continue
        # Drop bare numbers or placeholders like '21+'; handle separately
        if t.isdigit():
            continue
        if t.endswith("+") and t[:-1].isdigit():
            # 21+ → we will add adult/21yo below
            continue
        # Apply synonym mapping
        t = synonyms.get(t, t)
        # Drop generic gender words; handled via count tags
        if t in ("male", "female", "man", "woman"):
            continue
        # Normalize age tokens
        if t.endswith("yo") and t[:-2].isdigit():
            age = int(t[:-2])
            if age < 21:
                # Avoid minors; drop
                continue
            t = "21yo"
        elif t.isdigit():
            continue
        # Promote content flags
        if t == "nude":
            has_nude = True
        if t == "explicit":
            has_explicit = True
        if t == "penis":
            has_penis = True
        if t in ("erect", "erection"):
            has_erect = True
        if t in ("large", "big"):
            has_large = True
        if t == "blowjob":
            has_blowjob = True
        if t == "handjob":
            has_handjob = True
        if t in ("futa", "futanari", "shemale", "dickgirl"):
            has_futa = True

        # Accept tag
        if t and t not in seen:
            seen.add(t)
            out.append(t)

    # Ensure count tags if gender implied but no explicit count
    if not any(is_count_tag(t) for t in out):
        if has_female:
            if "1girl" not in seen:
                out.append("1girl")
                seen.add("1girl")
        if has_male:
            if "1boy" not in seen:
                out.append("1boy")
                seen.add("1boy")

    # If male present and nude, add nude_male descriptor
    if has_male and has_nude and "nude_male" not in seen:
        out.append("nude_male")
        seen.add("nude_male")

    # Compound heuristics for sexual acts
    if has_penis and has_erect and "erect_penis" not in seen:
        out.append("erect_penis")
        seen.add("erect_penis")
    if has_penis and has_large and "large_penis" not in seen:
        out.append("large_penis")
        seen.add("large_penis")
    if has_blowjob and "penis_in_mouth" not in seen:
        out.append("penis_in_mouth")
        seen.add("penis_in_mouth")
    if has_handjob and "penis_in_hand" not in seen:
        out.append("penis_in_hand")
        seen.add("penis_in_hand")
    if "anal_penetration" in seen and "penis_in_ass" not in seen:
        out.append("penis_in_ass")
        seen.add("penis_in_ass")
    if "penis_in_vagina" in seen and "vaginal_penetration" not in seen:
        out.append("vaginal_penetration")
        seen.add("vaginal_penetration")
    if "vaginal_penetration" in seen and "penis_in_vagina" not in seen:
        out.append("penis_in_vagina")
        seen.add("penis_in_vagina")

    # If futa-like subject present, ensure a canonical futa tag is included
    if has_futa and not any(t in seen for t in ("futa", "futanari", "shemale", "dickgirl")):
        out.append("futanari")
        seen.add("futanari")

    # Enforce adult + 21yo
    if "adult" not in seen:
        out.append("adult")
        seen.add("adult")
    if "21yo" not in seen:
        out.append("21yo")
        seen.add("21yo")

    # If nude/explicit, ensure nsfw
    if (has_nude or has_explicit) and "nsfw" not in seen:
        out.append("nsfw")
        added_nsfw = True

    # Keep quality tags at the very front, in order
    quality_order = ["score_9", "score_8_up", "score_7_up", "highly_detailed", "masterpiece", "best_quality"]
    quality_present = [q for q in quality_order if q in out]
    others = [t for t in out if t not in quality_present]
    return quality_present + others


def _canonicalize_negative_tags(tags: list[str]) -> list[str]:
    synonyms = {
        "low_res": "lowres",
        "bad_anatomy": "bad anatomy",
    }
    out: list[str] = []
    seen = set()
    for t in tags:
        if not t:
            continue
        t = synonyms.get(t, t)
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out

    @classmethod
    def IS_CHANGED(cls, **kwargs):  # Avoid caching across images/settings
        return True

NODE_CLASS_MAPPINGS = {
    "GrokPonyXLPrompter": GrokPonyXLPrompter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GrokPonyXLPrompter": "Grok PonyXL Prompter",
}
