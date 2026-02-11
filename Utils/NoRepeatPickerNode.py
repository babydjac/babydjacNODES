import os
import json
import random
import hashlib
from typing import Dict, Any, List


class NoRepeatPickerNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "items_text": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "randomize": ("BOOLEAN", {"default": True}),
                "item_index": ("INT", {"default": 0, "min": 0, "max": 1000000, "step": 1}),
                "persist_key": ("STRING", {"default": "default"}),
                "reuse_last": ("BOOLEAN", {"default": False}),
                "reset_history": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("item",)
    FUNCTION = "process"
    CATEGORY = "babydjacNODES/Utils"
    NODE_NAME = "NoRepeatPickerNode"

    def _state_path(self) -> str:
        base = os.path.dirname(__file__)
        return os.path.join(base, ".apk_no_repeat_state.json")

    def _load_state(self) -> Dict[str, Any]:
        p = self._state_path()
        try:
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save_state(self, st: Dict[str, Any]):
        p = self._state_path()
        try:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(st, f)
        except Exception:
            pass

    def _hash_items(self, items: List[str]) -> str:
        h = hashlib.sha256("\n".join(items).encode("utf-8")).hexdigest()
        return h

    def process(self, items_text: str, randomize: bool = True, item_index: int = 0, persist_key: str = "default", reuse_last: bool = False, reset_history: bool = False):
        items = [ln.strip() for ln in (items_text or "").splitlines() if ln.strip()]
        if not items:
            return ("",)

        state = self._load_state()
        sub = state.get(persist_key) or {"used": [], "last": None, "hash": None}

        cur_hash = self._hash_items(items)
        if reset_history or sub.get("hash") != cur_hash:
            sub = {"used": [], "last": None, "hash": cur_hash}

        if reuse_last and isinstance(sub.get("last"), int) and 0 <= sub["last"] < len(items):
            idx = sub["last"]
        else:
            if randomize:
                unused = [i for i in range(len(items)) if i not in set(sub["used"])]
                if not unused:
                    sub["used"] = []
                    unused = list(range(len(items)))
                idx = random.choice(unused)
            else:
                if item_index < 0:
                    item_index = 0
                idx = item_index % len(items)

        # update state
        sub["last"] = idx
        if not reuse_last:
            used = set(sub.get("used", []))
            used.add(idx)
            sub["used"] = sorted(list(used))
        state[persist_key] = sub
        self._save_state(state)

        return (items[idx],)

NODE_CLASS_MAPPINGS = {
    "NoRepeatPickerNode": NoRepeatPickerNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "NoRepeatPickerNode": "No-Repeat Picker",
}
