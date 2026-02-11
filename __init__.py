"""
babydjacNODES — Entry point
Registers all custom nodes in categories.
"""

# Loaders
from .Loaders.LoraFcKingLoader import LoraFcKingLoader

# Latents
from .Latents.InteractiveEmptyLatent import InteractiveEmptyLatent

# Prompting
from .Prompting.Z_Image.ZImagePromptEngineer import ZImagePromptEngineer
from .Prompting.Z_Image.ZImageTurboPromptEngineer import ZImageTurboPromptEngineer
from .Prompting.WAN_2_2.WAN22PromptStudioNode import WAN22PromptStudioNode
from .Prompting.Flux.FluxPromptBuilder import FluxPromptBuilder
from .Prompting.Flux.FluxDualPromptNode import FluxDualPromptNode
from .Prompting.Flux.FluxLifestylePromptNode import FluxLifestylePromptNode
from .Prompting.Flux.FluxLambdaPrompter import FluxLambdaPrompter
from .Prompting.PonyXL.GrokPonyXLPrompter import GrokPonyXLPrompter
from .Prompting.PonyXL.NSFWGrokToPonyXL import NSFWGrokToPonyXL
from .Prompting.QwenImagePrompter import QwenImagePrompter

# Analyze
from .Analyze.NSFWGrokDescriberPro import NSFWGrokDescriberPro
from .Analyze.GrokFluxPromptOptimizer import GrokFluxPromptOptimizer

# Taglists
from .Taglists.SafeTagListPromptNode import SafeTagListPromptNode
from .Taglists.TemplateDrivenTagListPromptNode import TemplateDrivenTagListPromptNode
from .Taglists.TagListPromptNode import TagListPromptNode

# Utils
from .Utils.PromptMergeNode import PromptMergeNode
from .Utils.DynamicPromptBatcher import DynamicPromptBatcher
from .Utils.TaglistSanitizerNode import TaglistSanitizerNode
from .Utils.WeightAdjustNode import WeightAdjustNode
from .Utils.NoRepeatPickerNode import NoRepeatPickerNode
from .Utils.TextCacheNode import TextCacheNode
from .Utils.HTTPJsonNode import HTTPJsonNode
from .Utils.NSFWGrokFusionPro import NSFWGrokFusionPro

NODE_CLASS_MAPPINGS = {
    # Loaders
    "LoraFcKingLoader": LoraFcKingLoader,

    # Latents
    "InteractiveEmptyLatent": InteractiveEmptyLatent,

    # Prompting
    "ZImagePromptEngineer": ZImagePromptEngineer,
    "ZImageTurboPromptEngineer": ZImageTurboPromptEngineer,
    "WAN22PromptStudioNode": WAN22PromptStudioNode,
    "FluxPromptBuilder": FluxPromptBuilder,
    "FluxDualPromptNode": FluxDualPromptNode,
    "FluxLifestylePromptNode": FluxLifestylePromptNode,
    "FluxLambdaPrompter": FluxLambdaPrompter,
    "GrokPonyXLPrompter": GrokPonyXLPrompter,
    "NSFWGrokToPonyXL": NSFWGrokToPonyXL,
    "QwenImagePrompter": QwenImagePrompter,

    # Analyze
    "NSFWGrokDescriberPro": NSFWGrokDescriberPro,
    "GrokFluxPromptOptimizer": GrokFluxPromptOptimizer,

    # Taglists
    "SafeTagListPromptNode": SafeTagListPromptNode,
    "TemplateDrivenTagListPromptNode": TemplateDrivenTagListPromptNode,
    "TagListPromptNode": TagListPromptNode,

    # Utils
    "PromptMergeNode": PromptMergeNode,
    "TaglistSanitizerNode": TaglistSanitizerNode,
    "WeightAdjustNode": WeightAdjustNode,
    "NoRepeatPickerNode": NoRepeatPickerNode,
    "TextCacheNode": TextCacheNode,
    "HTTPJsonNode": HTTPJsonNode,
    "NSFWGrokFusionPro": NSFWGrokFusionPro,
    "DynamicPromptBatcher": DynamicPromptBatcher,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LoraFcKingLoader": "LoraFcKingLoader",
    "InteractiveEmptyLatent": "Latent Size Controller",
    "ZImagePromptEngineer": "Z-Image Prompt Engineer",
    "ZImageTurboPromptEngineer": "Z-Image Turbo Prompt Engineer",
    "WAN22PromptStudioNode": "WAN 2.2 Prompt Studio",
    "FluxPromptBuilder": "Flux Prompt Builder",
    "FluxDualPromptNode": "Flux Dual Prompt Node (Grok)",
    "FluxLifestylePromptNode": "Flux Lifestyle Prompt Node",
    "FluxLambdaPrompter": "Flux Lambda Prompter",
    "GrokPonyXLPrompter": "Grok PonyXL Prompter",
    "NSFWGrokToPonyXL": "Grok to PonyXL Prompt",
    "QwenImagePrompter": "Qwen Image Prompter",
    "NSFWGrokDescriberPro": "Grok Image Describer Pro",
    "GrokFluxPromptOptimizer": "Grok Flux Prompt Optimizer",
    "SafeTagListPromptNode": "Safe Tag List Prompt",
    "TemplateDrivenTagListPromptNode": "Template Driven Taglist",
    "TagListPromptNode": "Taglist Prompt",
    "PromptMergeNode": "Prompt Merge",
    "TaglistSanitizerNode": "Taglist Sanitizer",
    "WeightAdjustNode": "Weight Adjust",
    "NoRepeatPickerNode": "No-Repeat Picker",
    "TextCacheNode": "Text Cache",
    "HTTPJsonNode": "HTTP JSON",
    "NSFWGrokFusionPro": "Grok Prompt Fusion Pro",
    "DynamicPromptBatcher": "Prompt Rotator (Dynamic Batch)",
}

WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
