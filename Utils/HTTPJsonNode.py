import json
import requests


class HTTPJsonNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url": ("STRING", {"default": "", "multiline": False}),
            },
            "optional": {
                "method": ("CHOICE", {"choices": ["GET", "POST", "PUT", "PATCH", "DELETE"], "default": "GET"}),
                "headers_json": ("STRING", {"default": "{}", "multiline": True}),
                "body": ("STRING", {"default": "", "multiline": True}),
                "timeout_sec": ("INT", {"default": 30, "min": 1, "max": 300, "step": 1}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("response_text",)
    FUNCTION = "process"
    CATEGORY = "babydjacNODES/Utils"
    NODE_NAME = "HTTPJsonNode"

    def process(self, url: str, method: str = "GET", headers_json: str = "{}", body: str = "", timeout_sec: int = 30):
        url = (url or "").strip()
        if not url:
            return ("",)
        try:
            headers = json.loads(headers_json) if headers_json else {}
            if not isinstance(headers, dict):
                headers = {}
        except Exception:
            headers = {}

        method = (method or "GET").upper()
        try:
            if method == "GET":
                r = requests.get(url, headers=headers, timeout=timeout_sec)
            elif method == "POST":
                r = requests.post(url, headers=headers, data=body, timeout=timeout_sec)
            elif method == "PUT":
                r = requests.put(url, headers=headers, data=body, timeout=timeout_sec)
            elif method == "PATCH":
                r = requests.patch(url, headers=headers, data=body, timeout=timeout_sec)
            elif method == "DELETE":
                r = requests.delete(url, headers=headers, data=body, timeout=timeout_sec)
            else:
                return ("",)
            r.raise_for_status()
            return (r.text,)
        except requests.exceptions.RequestException as e:
            return (f"HTTP error: {e}",)
        except Exception as e:
            return (f"Unexpected error: {e}",)

NODE_CLASS_MAPPINGS = {
    "HTTPJsonNode": HTTPJsonNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "HTTPJsonNode": "HTTP JSON",
}
