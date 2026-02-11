import re


class WeightAdjustNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "taglist": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "multiply": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.05}),
                "base_weight": ("FLOAT", {"default": 1.1, "min": 0.0, "max": 10.0, "step": 0.05}),
                "apply_to_unweighted": ("BOOLEAN", {"default": True}),
                "clamp_min": ("FLOAT", {"default": 0.1}),
                "clamp_max": ("FLOAT", {"default": 2.0}),
                "round_to": ("INT", {"default": 2, "min": 0, "max": 6, "step": 1}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("adjusted",)
    FUNCTION = "process"
    CATEGORY = "babydjacNODES/Utils"
    NODE_NAME = "WeightAdjustNode"

    def _split(self, text: str):
        return [p.strip() for p in text.replace("\n", ",").split(",") if p.strip()]

    def _parse_weight(self, token: str):
        m = re.match(r"^\((.+?):([0-9.]+)\)$", token.strip())
        if m:
            return m.group(1).strip(), float(m.group(2))
        return token.strip(), None

    def _wrap(self, token: str, w: float, round_to: int):
        fmt = f"{w:.{round_to}f}" if round_to >= 0 else str(w)
        return f"({token}:{fmt})"

    def process(self, taglist: str, multiply: float = 1.0, base_weight: float = 1.1, apply_to_unweighted: bool = True, clamp_min: float = 0.1, clamp_max: float = 2.0, round_to: int = 2):
        out = []
        for token in self._split(taglist):
            core, w = self._parse_weight(token)
            if w is None:
                if apply_to_unweighted:
                    w2 = max(clamp_min, min(clamp_max, base_weight * multiply))
                    out.append(self._wrap(core, w2, round_to))
                else:
                    out.append(core)
            else:
                w2 = max(clamp_min, min(clamp_max, w * multiply))
                out.append(self._wrap(core, w2, round_to))
        return (", ".join(out),)

NODE_CLASS_MAPPINGS = {
    "WeightAdjustNode": WeightAdjustNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WeightAdjustNode": "Weight Adjust",
}
