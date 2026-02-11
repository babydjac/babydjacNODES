from .SafeTagListPromptNode import SafeTagListPromptNode


class TagListPromptNode(SafeTagListPromptNode):
    """
    Taglist prompt node that inherits SafeTagListPromptNode behavior.
    """
    CATEGORY = "babydjacNODES/Taglists"
    NODE_NAME = "TagListPromptNode"

NODE_CLASS_MAPPINGS = {
    "TagListPromptNode": TagListPromptNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TagListPromptNode": "Taglist Prompt",
}
