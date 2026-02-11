# LoraFcKingLoader

- Node ID: `LoraFcKingLoader`
- Class: `LoraFcKingLoader`
- Category: `babydjacNODES/Loaders`
- Function: `load_stack`
- Module: `babydjacNODES.Loaders.LoraFcKingLoader`

## Purpose

Loads and stacks multiple LoRA files on top of a base model and CLIP, in slot order.

## Required Inputs

- `model`: `MODEL` (tooltip='Base diffusion model.')
- `clip`: `CLIP` (tooltip='Base CLIP model.')
- `lora_count`: `INT` (default=1; min=1; max=5; step=1)
- `enabled_1`: `BOOLEAN` (default=True)
- `lora_name_1`: COMBO (`None`) (default='None')
- `strength_model_1`: `FLOAT` (default=1.0; min=-100.0; max=100.0; step=0.01)
- `strength_clip_1`: `FLOAT` (default=1.0; min=-100.0; max=100.0; step=0.01)
- `enabled_2`: `BOOLEAN` (default=False)
- `lora_name_2`: COMBO (`None`) (default='None')
- `strength_model_2`: `FLOAT` (default=1.0; min=-100.0; max=100.0; step=0.01)
- `strength_clip_2`: `FLOAT` (default=1.0; min=-100.0; max=100.0; step=0.01)
- `enabled_3`: `BOOLEAN` (default=False)
- `lora_name_3`: COMBO (`None`) (default='None')
- `strength_model_3`: `FLOAT` (default=1.0; min=-100.0; max=100.0; step=0.01)
- `strength_clip_3`: `FLOAT` (default=1.0; min=-100.0; max=100.0; step=0.01)
- `enabled_4`: `BOOLEAN` (default=False)
- `lora_name_4`: COMBO (`None`) (default='None')
- `strength_model_4`: `FLOAT` (default=1.0; min=-100.0; max=100.0; step=0.01)
- `strength_clip_4`: `FLOAT` (default=1.0; min=-100.0; max=100.0; step=0.01)
- `enabled_5`: `BOOLEAN` (default=False)
- `lora_name_5`: COMBO (`None`) (default='None')
- `strength_model_5`: `FLOAT` (default=1.0; min=-100.0; max=100.0; step=0.01)
- `strength_clip_5`: `FLOAT` (default=1.0; min=-100.0; max=100.0; step=0.01)

## Outputs

- `MODEL`: `MODEL`
- `CLIP`: `CLIP`

## Minimal Usage

Set required inputs, then queue the workflow. Suggested starter values:

- `model` -> `<connect>`
- `clip` -> `<connect>`
- `lora_count` -> `1`
- `enabled_1` -> `True`
- `lora_name_1` -> `None`
- `strength_model_1` -> `1.0`
- `strength_clip_1` -> `1.0`
- `enabled_2` -> `False`
- `lora_name_2` -> `None`
- `strength_model_2` -> `1.0`
- `strength_clip_2` -> `1.0`
- `enabled_3` -> `False`
- `lora_name_3` -> `None`
- `strength_model_3` -> `1.0`
- `strength_clip_3` -> `1.0`
- `enabled_4` -> `False`
- `lora_name_4` -> `None`
- `strength_model_4` -> `1.0`
- `strength_clip_4` -> `1.0`
- `enabled_5` -> `False`
- `lora_name_5` -> `None`
- `strength_model_5` -> `1.0`
- `strength_clip_5` -> `1.0`

## Workflow Snippet

Minimal prompt JSON fragment (replace node ids/connections as needed):

```json
{
  "12": {
    "class_type": "LoraFcKingLoader",
    "inputs": {
      "model": "<connect>",
      "clip": "<connect>",
      "lora_count": 1,
      "enabled_1": true,
      "lora_name_1": "None",
      "strength_model_1": 1.0,
      "strength_clip_1": 1.0,
      "enabled_2": false,
      "lora_name_2": "None",
      "strength_model_2": 1.0,
      "strength_clip_2": 1.0,
      "enabled_3": false,
      "lora_name_3": "None",
      "strength_model_3": 1.0,
      "strength_clip_3": 1.0,
      "enabled_4": false,
      "lora_name_4": "None",
      "strength_model_4": 1.0,
      "strength_clip_4": 1.0,
      "enabled_5": false,
      "lora_name_5": "None",
      "strength_model_5": 1.0,
      "strength_clip_5": 1.0
    }
  }
}
```

## Notes

- Behavior and defaults are defined in the node source file.
- If this node depends on an external API, provide credentials through node inputs or environment variables as required.
