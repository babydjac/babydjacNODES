import folder_paths
import comfy.utils
import comfy.sd

MAX_LORAS = 5


def _lora_choices():
    names = folder_paths.get_filename_list("loras")
    if not names:
        return ["None"]
    if "None" not in names:
        return ["None"] + names
    return names


class LoraFcKingLoader:
    """
    Multi-LoRA loader with a dynamic UI. Applies up to MAX_LORAS LoRAs in order.
    """

    def __init__(self):
        self._cache = {}

    @classmethod
    def INPUT_TYPES(cls):
        required = {
            "model": ("MODEL", {"tooltip": "Base diffusion model."}),
            "clip": ("CLIP", {"tooltip": "Base CLIP model."}),
            "lora_count": ("INT", {"default": 1, "min": 1, "max": MAX_LORAS, "step": 1}),
        }

        # Build fixed widget set; JS hides unused slots dynamically.
        for i in range(1, MAX_LORAS + 1):
            required[f"enabled_{i}"] = ("BOOLEAN", {"default": True if i == 1 else False})
            required[f"lora_name_{i}"] = (_lora_choices(), {"default": "None"})
            required[f"strength_model_{i}"] = (
                "FLOAT",
                {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.01},
            )
            required[f"strength_clip_{i}"] = (
                "FLOAT",
                {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.01},
            )

        return {"required": required}

    RETURN_TYPES = ("MODEL", "CLIP")
    RETURN_NAMES = ("MODEL", "CLIP")
    FUNCTION = "load_stack"
    CATEGORY = "babydjacNODES/Loaders"
    NODE_NAME = "LoraFcKingLoader"
    WEB_DIRECTORY = "lora_fcking_loader"
    DESCRIPTION = (
        "Load and stack multiple LoRAs with per-slot strengths. "
        "Slots are applied in order; disabled slots are skipped."
    )

    def _load_lora(self, lora_name):
        if not lora_name or lora_name == "None":
            return None
        lora_path = folder_paths.get_full_path_or_raise("loras", lora_name)
        cached = self._cache.get(lora_path)
        if cached is not None:
            return cached
        lora = comfy.utils.load_torch_file(lora_path, safe_load=True)
        self._cache[lora_path] = lora
        return lora

    def load_stack(self, model, clip, lora_count, **kwargs):
        if lora_count < 1:
            return (model, clip)

        # Apply in order
        for i in range(1, MAX_LORAS + 1):
            if i > lora_count:
                break
            if not kwargs.get(f"enabled_{i}", False):
                continue

            lora_name = kwargs.get(f"lora_name_{i}", "None")
            strength_model = float(kwargs.get(f"strength_model_{i}", 0.0))
            strength_clip = float(kwargs.get(f"strength_clip_{i}", 0.0))

            if lora_name in (None, "None"):
                continue
            if strength_model == 0 and strength_clip == 0:
                continue

            lora = self._load_lora(lora_name)
            if lora is None:
                continue

            model, clip = comfy.sd.load_lora_for_models(
                model, clip, lora, strength_model, strength_clip
            )

        return (model, clip)



NODE_CLASS_MAPPINGS = {
    "LoraFcKingLoader": LoraFcKingLoader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoraFcKingLoader": "LoraFcKingLoader",
}
