import importlib.util
import sys
from pathlib import Path

import pytest
import torch


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
COMFY_ROOT = PLUGIN_ROOT.parents[1]

if str(COMFY_ROOT) not in sys.path:
    sys.path.insert(0, str(COMFY_ROOT))
if str(PLUGIN_ROOT.parent) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT.parent))


def _load_package():
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


PKG = _load_package()
SMALL_IMAGE = torch.zeros((1, 16, 16, 3), dtype=torch.float32)
MODEL_SENTINEL = object()
CLIP_SENTINEL = object()


SMOKE_OVERRIDES = {
    "DynamicPromptBatcher": {"prompt_1": "alpha"},
    "FluxPromptBuilder": {
        "subject": "portrait in studio",
        "use_grok": False,
        "guidance_tags": "sharp focus",
    },
    "HTTPJsonNode": {"url": "ftp://example.com/data.json"},
    "InteractiveEmptyLatent": {
        "width": 1001,
        "height": 997,
        "batch_size": 2,
        "model_profile": "SDXL",
        "snap_to": "64",
    },
    "LoraFcKingLoader": {
        "model": MODEL_SENTINEL,
        "clip": CLIP_SENTINEL,
        "lora_count": 0,
        "enabled_1": False,
    },
    "NoRepeatPickerNode": {
        "items_text": "alpha\nbeta\ngamma",
        "randomize": False,
        "item_index": 1,
    },
    "NSFWGrokFusionPro": {
        "base_prompt": "portrait, soft light",
        "second_prompt": "cinematic framing",
        "annotator": True,
    },
    "NSFWGrokToPonyXL": {"description": "studio portrait"},
    "PromptMergeNode": {
        "taglist_a": "A, B",
        "taglist_b": "b, C",
        "extra_taglist": "C, D",
        "dedupe": True,
        "lowercase": True,
    },
    "QwenImagePrompter": {"idea": "retro neon diner"},
    "SafeTagListPromptNode": {
        "template_text": "portrait, studio lighting",
        "custom_idea": "fashion shoot",
    },
    "TagListPromptNode": {
        "template_text": "portrait, studio lighting",
        "custom_idea": "fashion shoot",
    },
    "TaglistSanitizerNode": {
        "taglist": "A, (B:1.2), a",
        "lowercase": True,
        "strip_weights": True,
        "sort_alpha": True,
    },
    "TemplateDrivenTagListPromptNode": {
        "custom_template": "portrait, studio lighting",
        "custom_idea": "fashion shoot",
    },
    "TextCacheNode": {"mode": "set", "key": "greeting", "value": "hello"},
    "WAN22PromptStudioNode": {"user_idea": "moody cinematic street scene"},
    "WeightAdjustNode": {
        "taglist": "portrait, (sharp focus:1.5)",
        "multiply": 0.5,
        "apply_to_unweighted": True,
    },
    "ZImagePromptEngineer": {"text_input": "storm-lit alpine cabin at dawn"},
    "ZImageTurboPromptEngineer": {"text_input": "cyberpunk street racer"},
}


EXPECTED_EXCEPTIONS = {
    "FluxDualPromptNode": (ValueError, "API key is required"),
    "FluxLambdaPrompter": (ValueError, "API key is required"),
    "GrokPonyXLPrompter": (
        ValueError,
        "Missing API key",
    ),
}


@pytest.fixture(autouse=True)
def _block_network(monkeypatch):
    import requests

    def fail(*args, **kwargs):
        raise AssertionError("Unexpected network call in node smoke tests")

    for name in ("get", "post", "put", "patch", "delete"):
        monkeypatch.setattr(requests, name, fail)

    monkeypatch.delenv("XAI_API_KEY", raising=False)
    monkeypatch.delenv("GROK_API_KEY", raising=False)


def _value_from_spec(input_name, spec):
    kind = spec[0]
    opts = spec[1] if len(spec) > 1 and isinstance(spec[1], dict) else {}

    if isinstance(kind, list):
        return opts.get("default", kind[0])
    if kind == "STRING":
        if input_name.endswith("api_key") or input_name == "api_key":
            return ""
        default = opts.get("default")
        return default if default not in (None, "") else f"test {input_name}"
    if kind == "INT":
        return opts.get("default", 1)
    if kind == "FLOAT":
        return opts.get("default", 0.5)
    if kind == "BOOLEAN":
        return opts.get("default", False)
    if kind == "CHOICE":
        return opts.get("default", opts["choices"][0])
    if kind == "IMAGE":
        return SMALL_IMAGE
    if kind == "MODEL":
        return MODEL_SENTINEL
    if kind == "CLIP":
        return CLIP_SENTINEL
    raise AssertionError(f"Unhandled input type for {input_name}: {kind}")


def _build_kwargs(node_cls):
    schema = node_cls.INPUT_TYPES()
    kwargs = {}
    for input_name, spec in schema.get("required", {}).items():
        kwargs[input_name] = _value_from_spec(input_name, spec)
    return kwargs


def _prepare_node(monkeypatch, node_name, node):
    if node_name == "LoraFcKingLoader":
        lora_module = sys.modules["babydjacNODES.Loaders.LoraFcKingLoader"]
        monkeypatch.setattr(
            lora_module.folder_paths,
            "get_filename_list",
            lambda _kind: ["None"],
        )

    if node_name == "NoRepeatPickerNode":
        monkeypatch.setattr(
            node,
            "_state_path",
            lambda: str(PLUGIN_ROOT / "tests" / ".tmp_no_repeat_state.json"),
        )

    if node_name == "TextCacheNode":
        monkeypatch.setattr(
            node,
            "_path",
            lambda: str(PLUGIN_ROOT / "tests" / ".tmp_text_cache.json"),
        )


def _call_node(monkeypatch, node_name):
    node_cls = PKG.NODE_CLASS_MAPPINGS[node_name]
    node = node_cls()
    _prepare_node(monkeypatch, node_name, node)
    kwargs = _build_kwargs(node_cls)
    kwargs.update(SMOKE_OVERRIDES.get(node_name, {}))
    fn = getattr(node, node_cls.FUNCTION)
    return fn(**kwargs), node_cls


def test_node_registry_is_in_sync():
    assert len(PKG.NODE_CLASS_MAPPINGS) == 26
    assert set(PKG.NODE_CLASS_MAPPINGS) == set(PKG.NODE_DISPLAY_NAME_MAPPINGS)


@pytest.mark.parametrize("node_name", sorted(PKG.NODE_CLASS_MAPPINGS))
def test_each_registered_node_smoke(monkeypatch, node_name):
    if node_name in EXPECTED_EXCEPTIONS:
        exc_type, message = EXPECTED_EXCEPTIONS[node_name]
        with pytest.raises(exc_type, match=message):
            _call_node(monkeypatch, node_name)
        return

    result, node_cls = _call_node(monkeypatch, node_name)

    assert isinstance(result, tuple)
    assert len(result) == len(node_cls.RETURN_TYPES)


def test_interactive_empty_latent_snaps_and_shapes():
    node = PKG.NODE_CLASS_MAPPINGS["InteractiveEmptyLatent"]()
    latent, = node.generate(
        width=1001,
        height=997,
        batch_size=2,
        model_profile="SDXL",
        snap_to="64",
        ui_mode="graph",
        aspect_lock=False,
        preset="custom",
    )

    samples = latent["samples"]
    assert tuple(samples.shape) == (2, 4, 128, 128)


def test_http_json_rejects_non_http_schemes():
    node = PKG.NODE_CLASS_MAPPINGS["HTTPJsonNode"]()
    response_text, = node.process("ftp://example.com/data.json")
    assert "only http and https URLs" in response_text


def test_prompt_cleanup_nodes_transform_text():
    merge_node = PKG.NODE_CLASS_MAPPINGS["PromptMergeNode"]()
    merged, = merge_node.process(
        "A, B",
        "b, C",
        extra_taglist="C, D",
        dedupe=True,
        lowercase=True,
        sort_alpha=True,
    )
    assert merged == "a, b, c, d"

    sanitize_node = PKG.NODE_CLASS_MAPPINGS["TaglistSanitizerNode"]()
    sanitized, = sanitize_node.process(
        "A, (B:1.2), a",
        dedupe=True,
        lowercase=True,
        strip_weights=True,
        sort_alpha=True,
    )
    assert sanitized == "a, b"

    weight_node = PKG.NODE_CLASS_MAPPINGS["WeightAdjustNode"]()
    adjusted, = weight_node.process(
        "portrait, (sharp focus:1.5)",
        multiply=0.5,
        base_weight=1.1,
        apply_to_unweighted=True,
        clamp_min=0.1,
        clamp_max=2.0,
        round_to=2,
    )
    assert adjusted == "(portrait:0.55), (sharp focus:0.75)"


def test_text_cache_round_trip(monkeypatch, tmp_path):
    node = PKG.NODE_CLASS_MAPPINGS["TextCacheNode"]()
    cache_path = tmp_path / "text_cache.json"
    monkeypatch.setattr(node, "_path", lambda: str(cache_path))

    set_value, = node.process("set", "greeting", "hello", "demo")
    get_value, = node.process("get", "greeting", namespace="demo")
    delete_value, = node.process("delete", "greeting", namespace="demo")
    missing_value, = node.process("get", "greeting", namespace="demo")

    assert set_value == "hello"
    assert get_value == "hello"
    assert delete_value == ""
    assert missing_value == ""


def test_no_repeat_picker_supports_reuse_and_reset(monkeypatch, tmp_path):
    node = PKG.NODE_CLASS_MAPPINGS["NoRepeatPickerNode"]()
    state_path = tmp_path / "picker_state.json"
    monkeypatch.setattr(node, "_state_path", lambda: str(state_path))

    first, = node.process(
        "alpha\nbeta\ngamma",
        randomize=False,
        item_index=1,
        persist_key="demo",
    )
    reused, = node.process(
        "alpha\nbeta\ngamma",
        randomize=False,
        item_index=0,
        persist_key="demo",
        reuse_last=True,
    )
    reset_pick, = node.process(
        "alpha\nbeta\ngamma",
        randomize=False,
        item_index=2,
        persist_key="demo",
        reset_history=True,
    )

    assert first == "beta"
    assert reused == "beta"
    assert reset_pick == "gamma"


def test_flux_prompt_builder_works_without_api_key():
    node = PKG.NODE_CLASS_MAPPINGS["FluxPromptBuilder"]()
    positive, negative = node.generate(
        subject="portrait in studio",
        style="cinematic",
        camera="85mm",
        lighting="softbox",
        spice=0.6,
        safety_level="standard",
        use_grok=False,
        guidance_tags="sharp focus",
        forbidden_tags="lowres",
        prompt_override="",
    )

    assert "portrait in studio" in positive
    assert "camera: 85mm" in positive
    assert "explicit" in negative


def test_zimage_nodes_fall_back_to_local_logic():
    base_node = PKG.NODE_CLASS_MAPPINGS["ZImagePromptEngineer"]()
    turbo_node = PKG.NODE_CLASS_MAPPINGS["ZImageTurboPromptEngineer"]()

    base_result = base_node.process(
        text_input="storm-lit alpine cabin at dawn",
        prompt_length="Standard",
        style="Photorealistic",
        camera="None",
        lighting="None",
        framing="None",
        mood="None",
        color_palette="None",
        detail_focus="None",
        negative_focus="Artifacts",
        quality_preset="Production",
    )
    turbo_result = turbo_node.process(
        text_input="cyberpunk street racer",
        style="Photorealistic",
        camera="None",
        lighting="None",
        framing="None",
        quality_preset="Balanced",
    )

    assert len(base_result) == 6
    assert "Static Logic" in base_result[4]
    assert len(turbo_result) == 5
    assert "Static Logic" in turbo_result[3]
