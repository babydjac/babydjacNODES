import re
from typing import List


def _split_tags(text: str) -> List[str]:
    if not text:
        return []
    parts = [p.strip() for p in text.replace("\n", ",").split(",")]
    return [p for p in parts if p]


class PromptMergeNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "taglist_a": ("STRING", {"default": "", "multiline": True}),
                "taglist_b": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "extra_taglist": ("STRING", {"default": "", "multiline": True}),
                "dedupe": ("BOOLEAN", {"default": True}),
                "lowercase": ("BOOLEAN", {"default": False}),
                "sort_alpha": ("BOOLEAN", {"default": False}),
                "max_tokens": ("INT", {"default": 0, "min": 0, "max": 10000, "step": 1}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("merged",)
    FUNCTION = "process"
    CATEGORY = "babydjacNODES/Utils"
    NODE_NAME = "PromptMergeNode"

    def process(self, taglist_a: str, taglist_b: str, extra_taglist: str = "", dedupe: bool = True, lowercase: bool = False, sort_alpha: bool = False, max_tokens: int = 0):
        all_tags = _split_tags(taglist_a) + _split_tags(taglist_b) + _split_tags(extra_taglist)
        if lowercase:
            all_tags = [t.lower() for t in all_tags]
        if dedupe:
            seen = set()
            deduped = []
            for t in all_tags:
                key = re.sub(r"\s+", " ", t.strip())
                if key not in seen:
                    seen.add(key)
                    deduped.append(t.strip())
            all_tags = deduped
        if sort_alpha:
            all_tags = sorted(all_tags, key=lambda s: s.lower())
        if max_tokens and max_tokens > 0:
            all_tags = all_tags[:max_tokens]
        return (", ".join(all_tags),)

NODE_CLASS_MAPPINGS = {
    "PromptMergeNode": PromptMergeNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptMergeNode": "Prompt Merge",
}
