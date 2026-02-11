import torch


class InteractiveEmptyLatent:
    MODEL_PROFILES = (
        "WAN 2.1 / WAN 2.2",
        "SD 1.5",
        "SDXL",
        "Z-Image / Z-Image Turbo",
    )

    PROFILE_SNAP_DEFAULT = {
        "WAN 2.1 / WAN 2.2": 32,
        "SD 1.5": 64,
        "SDXL": 64,
        "Z-Image / Z-Image Turbo": 16,
    }

    PROFILE_MAX_SIZE = {
        "WAN 2.1 / WAN 2.2": 1536,
        "SD 1.5": 1024,
        "SDXL": 2048,
        "Z-Image / Z-Image Turbo": 2048,
    }

    PROFILE_PRESETS = {
        "WAN 2.1 / WAN 2.2": {
            "custom": None,
            "Low VRAM (480x480)": (480, 480),
            "Portrait Detail (480x832)": (480, 832),
            "Mid Detail (720x1280)": (720, 1280),
            "High Detail (1536x1536)": (1536, 1536),
        },
        "SD 1.5": {
            "custom": None,
            "Base (512x512)": (512, 512),
            "High Quality (768x768)": (768, 768),
            "Landscape (768x512)": (768, 512),
            "Portrait (512x768)": (512, 768),
            "Wide (896x512)": (896, 512),
            "Tall (512x896)": (512, 896),
        },
        "SDXL": {
            "custom": None,
            "Base (1024x1024)": (1024, 1024),
            "Portrait (896x1152)": (896, 1152),
            "Landscape (1152x896)": (1152, 896),
            "Tall Portrait (768x1344)": (768, 1344),
            "Wide Landscape (1344x768)": (1344, 768),
            "Tall (768x1152)": (768, 1152),
            "Horizontal (1152x768)": (1152, 768),
        },
        "Z-Image / Z-Image Turbo": {
            "custom": None,
            "Ultra Fast (512x512)": (512, 512),
            "Fast Square (720x720)": (720, 720),
            "Balanced Vertical (720x1280)": (720, 1280),
            "Balanced Square (1024x1024)": (1024, 1024),
            "High Quality (1344x1344)": (1344, 1344),
        },
    }

    @classmethod
    def INPUT_TYPES(cls):
        all_presets = ["custom"]
        for profile in cls.MODEL_PROFILES:
            for preset in cls.PROFILE_PRESETS[profile].keys():
                if preset not in all_presets:
                    all_presets.append(preset)
        return {
            "required": {
                "width": ("INT", {"default": 1024, "min": 64, "max": 2048, "step": 8}),
                "height": ("INT", {"default": 1024, "min": 64, "max": 2048, "step": 8}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 16}),
                "model_profile": (list(cls.MODEL_PROFILES), {"default": "SDXL"}),
                "snap_to": (["auto", "8", "16", "32", "64"], {"default": "auto"}),
                "ui_mode": (["graph", "histogram"], {"default": "graph"}),
                "aspect_lock": ("BOOLEAN", {"default": False}),
                "preset": (all_presets, {"default": "custom"}),
            }
        }

    RETURN_TYPES = ("LATENT",)
    RETURN_NAMES = ("latent",)
    FUNCTION = "generate"
    CATEGORY = "babydjacNODES/Latents/Interactive"
    WEB_DIRECTORY = "interactive_empty_latent"

    def generate(
        self,
        width,
        height,
        batch_size,
        model_profile="SDXL",
        snap_to="auto",
        ui_mode="graph",
        aspect_lock=False,
        preset="custom",
    ):
        _ = (ui_mode, aspect_lock)  # UI-only controls, included for serialization and frontend behavior.

        profile_presets = self.PROFILE_PRESETS.get(model_profile, self.PROFILE_PRESETS["SDXL"])
        preset_size = profile_presets.get(preset)
        if preset_size is not None:
            width, height = preset_size

        if str(snap_to).lower() == "auto":
            snap = self.PROFILE_SNAP_DEFAULT.get(model_profile, 8)
        else:
            snap = int(snap_to)

        snap = max(8, snap)
        model_max = int(self.PROFILE_MAX_SIZE.get(model_profile, 2048))
        max_size = max(64, min(2048, model_max))
        width = max(64, min(max_size, int(width)))
        height = max(64, min(max_size, int(height)))
        width = max(snap, int(round(width / snap) * snap))
        height = max(snap, int(round(height / snap) * snap))

        # Latent space is 1/8 pixel space. Ensure valid latent dimensions.
        width = max(8, width - width % 8)
        height = max(8, height - height % 8)

        latent_w = width // 8
        latent_h = height // 8

        try:
            import comfy.model_management as mm

            device = mm.intermediate_device()
        except Exception:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        latent = torch.zeros([batch_size, 4, latent_h, latent_w], device=device, dtype=torch.float32)

        return ({"samples": latent},)


NODE_CLASS_MAPPINGS = {
    "InteractiveEmptyLatent": InteractiveEmptyLatent,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "InteractiveEmptyLatent": "Latent Size Controller",
}
