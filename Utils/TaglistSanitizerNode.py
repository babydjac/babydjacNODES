import re


class TaglistSanitizerNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "taglist": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "dedupe": ("BOOLEAN", {"default": True}),
                "lowercase": ("BOOLEAN", {"default": False}),
                "strip_weights": ("BOOLEAN", {"default": False}),
                "sort_alpha": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("sanitized",)
    FUNCTION = "process"
    CATEGORY = "babydjacNODES/Utils"
    NODE_NAME = "TaglistSanitizerNode"

    def _split(self, text: str):
        return [p.strip() for p in text.replace("\n", ",").split(",") if p.strip()]

    def _strip_weight(self, token: str) -> str:
        m = re.match(r"^\((.+?):[0-9.]+\)$", token.strip())
        return m.group(1).strip() if m else token.strip()

    def process(self, taglist: str, dedupe: bool = True, lowercase: bool = False, strip_weights: bool = False, sort_alpha: bool = False):
        tags = self._split(taglist)
        if strip_weights:
            tags = [self._strip_weight(t) for t in tags]
        if lowercase:
            tags = [t.lower() for t in tags]
        # normalize spaces
        tags = [re.sub(r"\s+", " ", t).strip() for t in tags]
        if dedupe:
            seen = set()
            out = []
            for t in tags:
                if t not in seen:
                    seen.add(t)
                    out.append(t)
            tags = out
        if sort_alpha:
            tags = sorted(tags, key=lambda s: s.lower())
        return (", ".join(tags),)

NODE_CLASS_MAPPINGS = {
    "TaglistSanitizerNode": TaglistSanitizerNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TaglistSanitizerNode": "Taglist Sanitizer",
}
