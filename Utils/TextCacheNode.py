import os
import json
from typing import Dict, Any


class TextCacheNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mode": ("CHOICE", {"choices": ["get", "set", "delete"], "default": "get"}),
                "key": ("STRING", {"default": "", "multiline": False}),
            },
            "optional": {
                "value": ("STRING", {"default": "", "multiline": True}),
                "namespace": ("STRING", {"default": "default"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("value",)
    FUNCTION = "process"
    CATEGORY = "babydjacNODES/Utils"
    NODE_NAME = "TextCacheNode"

    def _path(self) -> str:
        base = os.path.dirname(__file__)
        return os.path.join(base, ".apk_text_cache.json")

    def _load(self) -> Dict[str, Any]:
        p = self._path()
        try:
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save(self, obj: Dict[str, Any]):
        p = self._path()
        try:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(obj, f)
        except Exception:
            pass

    def process(self, mode: str, key: str, value: str = "", namespace: str = "default"):
        key = (key or "").strip()
        ns = (namespace or "default").strip()
        db = self._load()
        ns_db = db.get(ns) or {}

        if mode == "get":
            return (ns_db.get(key, ""),)
        elif mode == "set":
            ns_db[key] = value
            db[ns] = ns_db
            self._save(db)
            return (value,)
        elif mode == "delete":
            if key in ns_db:
                ns_db.pop(key)
                db[ns] = ns_db
                self._save(db)
            return ("",)
        else:
            return ("",)

NODE_CLASS_MAPPINGS = {
    "TextCacheNode": TextCacheNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TextCacheNode": "Text Cache",
}
