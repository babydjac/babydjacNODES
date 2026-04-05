import importlib.util
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from textwrap import wrap

import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
COMFY_ROOT = PLUGIN_ROOT.parents[1]
ASSET_ROOT = PLUGIN_ROOT / "assets" / "demos"
FRAME_ROOT = ASSET_ROOT / "frames"

if str(COMFY_ROOT) not in sys.path:
    sys.path.insert(0, str(COMFY_ROOT))
if str(PLUGIN_ROOT.parent) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT.parent))


def load_package():
    name = "babydjacNODES"
    if name in sys.modules:
        return sys.modules[name]

    spec = importlib.util.spec_from_file_location(
        name,
        PLUGIN_ROOT / "__init__.py",
        submodule_search_locations=[str(PLUGIN_ROOT)],
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


PKG = load_package()
API_KEY = (os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY") or "").strip()
LAMBDA_API_KEY = os.getenv("LAMBDA_API_KEY", "").strip()


@dataclass
class DemoResult:
    node_name: str
    display_name: str
    category: str
    mode: str
    status: str
    input_summary: str
    output_summary: str
    error: str = ""


def make_sample_image(width: int = 96, height: int = 96) -> torch.Tensor:
    x = np.linspace(0, 1, width, dtype=np.float32)
    y = np.linspace(0, 1, height, dtype=np.float32)
    xx, yy = np.meshgrid(x, y)
    rgb = np.stack([xx, yy, 1.0 - xx * 0.5], axis=-1)
    return torch.from_numpy(rgb).unsqueeze(0)


SAMPLE_IMAGE = make_sample_image()
MODEL_SENTINEL = object()
CLIP_SENTINEL = object()


def summarize_value(node_name: str, value) -> str:
    if isinstance(value, dict):
        if "samples" in value and hasattr(value["samples"], "shape"):
            return f"latent tensor shape={tuple(value['samples'].shape)}"
        return f"dict keys={list(value.keys())[:4]}"

    if isinstance(value, list):
        preview = ", ".join(str(item) for item in value[:4])
        return f"list[{len(value)}]: {preview}"

    if isinstance(value, (int, float, bool)):
        return repr(value)

    if value is MODEL_SENTINEL:
        return "MODEL passthrough"
    if value is CLIP_SENTINEL:
        return "CLIP passthrough"

    text = str(value).strip().replace("\n", " ")
    if not text:
        return "[empty]"

    # Keep README/demo assets safe and compact for explicit-oriented nodes.
    masked_nodes = {"NSFWGrokDescriber", "NSFWGrokDescriberPro", "NSFWGrokFusionPro", "NSFWGrokToPonyXL", "GrokPonyXLPrompter"}
    if node_name in masked_nodes:
        return f"text output captured ({len(text)} chars)"

    if len(text) > 160:
        text = text[:157] + "..."
    return text


def summarize_result(node_name: str, result) -> str:
    if not isinstance(result, tuple):
        return summarize_value(node_name, result)
    parts = [summarize_value(node_name, item) for item in result]
    return " | ".join(parts)


def redact_inputs(kwargs: dict) -> str:
    pairs = []
    for key, value in kwargs.items():
        if key in {"api_key", "grok_api_key"}:
            value = "[redacted]"
        pairs.append(f"{key}={value!r}")
    return ", ".join(pairs)


def get_font(size: int):
    candidates = [
        "/System/Library/Fonts/Supplemental/Menlo.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


TITLE_FONT = get_font(42)
SUBTITLE_FONT = get_font(24)
BODY_FONT = get_font(22)
SMALL_FONT = get_font(18)


def make_card(title: str, subtitle: str, body: str, footer: str, color: tuple[int, int, int]) -> Image.Image:
    width, height = 1280, 720
    image = Image.new("RGB", (width, height), (14, 18, 28))
    draw = ImageDraw.Draw(image)

    # Subtle vertical bands for motion when stitched into clips.
    for y in range(height):
        alpha = y / max(height - 1, 1)
        band = (
            min(255, int(14 + color[0] * 0.20 + alpha * 16)),
            min(255, int(18 + color[1] * 0.20 + alpha * 18)),
            min(255, int(28 + color[2] * 0.20 + alpha * 24)),
        )
        draw.line((0, y, width, y), fill=band)

    draw.rounded_rectangle((56, 48, width - 56, height - 48), radius=28, outline=(90, 104, 132), width=3, fill=(18, 22, 34))
    draw.rounded_rectangle((76, 72, 420, 128), radius=18, fill=color)
    draw.text((96, 84), "babydjacNODES demo", font=SUBTITLE_FONT, fill=(245, 248, 252))
    draw.text((76, 160), title, font=TITLE_FONT, fill=(245, 248, 252))
    draw.text((76, 222), subtitle, font=SUBTITLE_FONT, fill=(170, 184, 205))

    y = 292
    for paragraph in body.split("\n"):
        for line in wrap(paragraph, width=74) or [""]:
            draw.text((76, y), line, font=BODY_FONT, fill=(225, 232, 242))
            y += 34
        y += 10

    draw.text((76, height - 100), footer, font=SMALL_FONT, fill=(170, 184, 205))
    return image


def save_demo_clip(result: DemoResult):
    slug = result.node_name
    node_frame_dir = FRAME_ROOT / slug
    node_frame_dir.mkdir(parents=True, exist_ok=True)

    colors = {
        "ok": (41, 140, 94),
        "blocked": (158, 116, 31),
        "error": (150, 60, 64),
    }
    color = colors.get(result.status, colors["ok"])

    frames = [
        make_card(
            result.display_name,
            f"{result.category} | mode: {result.mode}",
            "Automated demo run generated for this node.",
            f"Node id: {result.node_name}",
            color,
        ),
        make_card(
            result.display_name,
            "Sample input",
            result.input_summary,
            "Input set used for automated validation/demo capture.",
            color,
        ),
        make_card(
            result.display_name,
            f"Run status: {result.status}",
            result.output_summary if result.status != "error" else result.error,
            "Output excerpt is abbreviated for README-safe previews.",
            color,
        ),
    ]

    frame_paths = []
    for idx, frame in enumerate(frames, start=1):
        frame_path = node_frame_dir / f"{idx:02d}.png"
        frame.save(frame_path)
        frame_paths.append(frame_path)

    gif_path = ASSET_ROOT / f"{slug}.gif"
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=[1200, 1200, 1800],
        loop=0,
    )

    mp4_path = ASSET_ROOT / f"{slug}.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(gif_path),
            "-movflags",
            "faststart",
            "-pix_fmt",
            "yuv420p",
            str(mp4_path),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def run_local(node_name: str, **kwargs) -> DemoResult:
    node_cls = PKG.NODE_CLASS_MAPPINGS[node_name]
    node = node_cls()
    fn = getattr(node, node_cls.FUNCTION)
    result = fn(**kwargs)
    return DemoResult(
        node_name=node_name,
        display_name=PKG.NODE_DISPLAY_NAME_MAPPINGS[node_name],
        category=node_cls.CATEGORY,
        mode="local",
        status="ok",
        input_summary=redact_inputs(kwargs),
        output_summary=summarize_result(node_name, result),
    )


def run_xai(node_name: str, **kwargs) -> DemoResult:
    if not API_KEY:
        node_cls = PKG.NODE_CLASS_MAPPINGS[node_name]
        return DemoResult(
            node_name=node_name,
            display_name=PKG.NODE_DISPLAY_NAME_MAPPINGS[node_name],
            category=node_cls.CATEGORY,
            mode="xai",
            status="blocked",
            input_summary=redact_inputs({k: v for k, v in kwargs.items() if k != "api_key"}),
            output_summary="Blocked: no XAI_API_KEY or GROK_API_KEY found in the environment.",
            error="Missing xAI key",
        )

    kwargs = dict(kwargs)
    if "api_key" in kwargs:
        kwargs["api_key"] = API_KEY
    if "grok_api_key" in kwargs:
        kwargs["grok_api_key"] = API_KEY
    result = run_local(node_name, **kwargs)
    result.mode = "xai"
    return result


def run_result(node_name: str, runner):
    node_cls = PKG.NODE_CLASS_MAPPINGS[node_name]
    try:
        result = runner()
        result.mode = result.mode
        return result
    except Exception as exc:
        return DemoResult(
            node_name=node_name,
            display_name=PKG.NODE_DISPLAY_NAME_MAPPINGS[node_name],
            category=node_cls.CATEGORY,
            mode="local",
            status="error",
            input_summary="See script runner configuration.",
            output_summary="Execution failed.",
            error=str(exc),
        )


def blocked_result(node_name: str, mode: str, reason: str, inputs: str) -> DemoResult:
    node_cls = PKG.NODE_CLASS_MAPPINGS[node_name]
    return DemoResult(
        node_name=node_name,
        display_name=PKG.NODE_DISPLAY_NAME_MAPPINGS[node_name],
        category=node_cls.CATEGORY,
        mode=mode,
        status="blocked",
        input_summary=inputs,
        output_summary=reason,
        error=reason,
    )


def node_runners():
    return {
        "DynamicPromptBatcher": lambda: run_local("DynamicPromptBatcher", prompt_1="portrait prompt", prompt_2="editorial prompt", prompt_3="sunset prompt"),
        "FluxDualPromptNode": lambda: run_xai("FluxDualPromptNode", api_key="", idea="cinematic portrait in a rain-soaked neon alley", model="grok-3-latest", temperature=0.4),
        "FluxLambdaPrompter": lambda: blocked_result(
            "FluxLambdaPrompter",
            "lambda",
            "Blocked: this node needs a Lambda API key, which was not provided in the environment.",
            "subject_scene='playful kitten with yarn balls'",
        )
        if not LAMBDA_API_KEY
        else run_local("FluxLambdaPrompter", api_key=LAMBDA_API_KEY, subject_scene="playful kitten with yarn balls", model="llama-4-maverick-17b-128e-instruct-fp8", temperature=0.5),
        "FluxLifestylePromptNode": lambda: run_xai("FluxLifestylePromptNode", prompt="cozy lifestyle portrait in a bright cafe", api_key=""),
        "FluxPromptBuilder": lambda: run_local("FluxPromptBuilder", subject="portrait in studio", style="cinematic", camera="85mm", lighting="softbox", spice=0.45, safety_level="standard", use_grok=False, guidance_tags="sharp focus", forbidden_tags="lowres", prompt_override=""),
        "GrokFluxPromptOptimizer": lambda: run_xai("GrokFluxPromptOptimizer", image=SAMPLE_IMAGE, user_instruction="make it brighter and more cinematic", api_key="", style_preference="cinematic", detail_level="basic"),
        "GrokPonyXLPrompter": lambda: run_xai("GrokPonyXLPrompter", image=SAMPLE_IMAGE, api_key="", exaggeration=1, add_realism_tags=False, quality_boost=False, custom_negatives="", extra_tags="landscape, scenic", instruction="Describe this as a safe scenic photography prompt.", max_tokens=96, temperature=0.2, top_p=0.9, frequency_penalty=0.0, presence_penalty=0.0, shuffle_order=False),
        "HTTPJsonNode": lambda: run_local("HTTPJsonNode", url="https://httpbin.org/json", method="GET", headers_json="{}", body="", timeout_sec=20),
        "InteractiveEmptyLatent": lambda: run_local("InteractiveEmptyLatent", width=1024, height=1024, batch_size=1, model_profile="SDXL", snap_to="auto", ui_mode="graph", aspect_lock=False, preset="Base (1024x1024)"),
        "LoraFcKingLoader": lambda: run_local("LoraFcKingLoader", model=MODEL_SENTINEL, clip=CLIP_SENTINEL, lora_count=0),
        "NSFWGrokDescriber": lambda: run_xai("NSFWGrokDescriber", image=SAMPLE_IMAGE, api_key=""),
        "NSFWGrokDescriberPro": lambda: run_xai("NSFWGrokDescriberPro", image=SAMPLE_IMAGE, api_key="", prepend_text="clean photo", append_text="natural light", score_strategy="ascending", debug_output="disable"),
        "NSFWGrokFusionPro": lambda: run_local("NSFWGrokFusionPro", base_prompt="portrait, soft light", strategy="balanced", tag_weight=1.0, preset="Cinematic", annotator=True, second_prompt="city skyline", blend_weight=0.3, auto_cycle=False, cycle_styles="", base_negative=""),
        "NSFWGrokToPonyXL": lambda: run_xai("NSFWGrokToPonyXL", description="editorial studio portrait with soft light", api_key="", motion_type="hair moving gently"),
        "NoRepeatPickerNode": lambda: run_local("NoRepeatPickerNode", items_text="alpha\nbeta\ngamma", randomize=False, item_index=1, persist_key="demo_assets", reuse_last=False, reset_history=True),
        "PromptMergeNode": lambda: run_local("PromptMergeNode", taglist_a="portrait, studio", taglist_b="soft light, portrait", extra_taglist="editorial", dedupe=True, lowercase=False, sort_alpha=True, max_tokens=0),
        "QwenImagePrompter": lambda: run_xai("QwenImagePrompter", idea="retro diner poster with the words \"OPEN LATE\"", api_key=""),
        "SafeTagListPromptNode": lambda: run_xai("SafeTagListPromptNode", template_text="portrait, studio lighting, editorial framing", custom_idea="confident fashion portrait with clean background", api_key="", model_name="grok-3-latest", temperature=0.2, safe_mode=True, blocklist="nsfw, explicit"),
        "TagListPromptNode": lambda: run_xai("TagListPromptNode", template_text="portrait, studio lighting, editorial framing", custom_idea="confident fashion portrait with clean background", api_key="", model_name="grok-3-latest", temperature=0.2, safe_mode=True, blocklist="nsfw, explicit"),
        "TaglistSanitizerNode": lambda: run_local("TaglistSanitizerNode", taglist="Portrait, (Sharp Focus:1.2), portrait", dedupe=True, lowercase=True, strip_weights=True, sort_alpha=True),
        "TemplateDrivenTagListPromptNode": lambda: run_xai("TemplateDrivenTagListPromptNode", template_name="<no-templates-found>", custom_template="portrait, studio lighting, editorial framing", custom_idea="confident fashion portrait with clean background", api_key="", model_name="grok-3-latest", temperature=0.2, safe_mode=True, blocklist="nsfw, explicit"),
        "TextCacheNode": lambda: run_local("TextCacheNode", mode="set", key="demo", value="hello world", namespace="demos"),
        "WAN22PromptStudioNode": lambda: run_xai("WAN22PromptStudioNode", user_idea="slow cinematic walk through a rainy neon street", grok_model="grok-2-vision-1212", content_mode="SFW", prompt_complexity="Advanced", style_preference="Cinematic", motion_intensity="Moderate", camera_style="Smooth Movement", lighting_mood="Atmospheric", color_palette="Cool", shot_type="Medium", time_of_day="Night", temperature=0.4, api_key="", specific_subject="single subject in coat", environment="city street", mood_keywords="moody, reflective", technical_specs="24fps feel"),
        "WeightAdjustNode": lambda: run_local("WeightAdjustNode", taglist="portrait, (sharp focus:1.5)", multiply=0.5, base_weight=1.1, apply_to_unweighted=True, clamp_min=0.1, clamp_max=2.0, round_to=2),
        "ZImagePromptEngineer": lambda: run_xai("ZImagePromptEngineer", text_input="storm-lit alpine cabin at dawn", prompt_length="Standard", style="Photorealistic", camera="None", lighting="None", framing="None", mood="None", color_palette="None", detail_focus="None", negative_focus="Artifacts", quality_preset="Production", must_include="mountains", avoid="blur", grok_api_key="", grok_model="grok-2-vision-1212"),
        "ZImageTurboPromptEngineer": lambda: run_xai("ZImageTurboPromptEngineer", text_input="cyberpunk street racer at dusk", style="Ultra-sharp hyperrealism", camera="None", lighting="None", framing="None", quality_preset="Balanced", grok_api_key="", grok_model="grok-2-vision-1212"),
    }


def patch_local_helpers():
    lora_module = sys.modules["babydjacNODES.Loaders.LoraFcKingLoader"]
    lora_module.folder_paths.get_filename_list = lambda _kind: ["None"]

    picker_cls = PKG.NODE_CLASS_MAPPINGS["NoRepeatPickerNode"]
    cache_cls = PKG.NODE_CLASS_MAPPINGS["TextCacheNode"]

    picker_cls._state_path = lambda self: str(ASSET_ROOT / ".demo_no_repeat_state.json")
    cache_cls._path = lambda self: str(ASSET_ROOT / ".demo_text_cache.json")


def main():
    ASSET_ROOT.mkdir(parents=True, exist_ok=True)
    FRAME_ROOT.mkdir(parents=True, exist_ok=True)
    patch_local_helpers()

    results = []
    for node_name in sorted(PKG.NODE_CLASS_MAPPINGS):
        runner = node_runners()[node_name]
        result = run_result(node_name, runner)
        results.append(result)
        save_demo_clip(result)
        print(f"{node_name}: {result.status}")

    manifest = {
        "generated_with_xai_key": bool(API_KEY),
        "generated_with_lambda_key": bool(LAMBDA_API_KEY),
        "results": [result.__dict__ for result in results],
    }
    (ASSET_ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
