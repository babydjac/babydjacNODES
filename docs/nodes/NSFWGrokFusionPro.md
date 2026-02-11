# NSFW Grok Fusion Pro

- Node ID: `NSFWGrokFusionPro`
- Class: `NSFWGrokFusionPro`
- Category: `babydjacNODES/Utils`
- Function: `generate`
- Module: `babydjacNODES.Utils.NSFWGrokFusionPro`

## Purpose

Combines and weights multiple prompt fragments with style presets and annotation output.

## Required Inputs

- `base_prompt`: `STRING` (default=''; multiline=True)
- `strategy`: COMBO (`beginner, balanced, expert, photorealism_max`) (default='balanced')
- `tag_weight`: `FLOAT` (default=1.0; min=0.1; max=2.0; step=0.1)
- `preset`: COMBO (`None, Softcore, Hardcore Realism, Cinematic, Studio Lighting`) (default='None')
- `annotator`: `BOOLEAN` (default=False)
- `second_prompt`: `STRING` (default=''; multiline=True)
- `blend_weight`: `FLOAT` (default=0.5; min=0.0; max=1.0; step=0.1)
- `auto_cycle`: `BOOLEAN` (default=False)
- `cycle_styles`: `STRING` (default=''; multiline=True)

## Optional Inputs

- `base_negative`: `STRING` (default=''; multiline=True)

## Hidden Inputs

- `unique_id`: `UNIQUE_ID`

## Outputs

- `positive_prompt`: `STRING`
- `negative_prompt`: `STRING`
- `annotation`: `STRING`

## Minimal Usage

Set required inputs, then queue the workflow. Suggested starter values:

- `base_prompt` -> ``
- `strategy` -> `balanced`
- `tag_weight` -> `1.0`
- `preset` -> `None`
- `annotator` -> `False`
- `second_prompt` -> ``
- `blend_weight` -> `0.5`
- `auto_cycle` -> `False`
- `cycle_styles` -> ``

## Workflow Snippet

Minimal prompt JSON fragment (replace node ids/connections as needed):

```json
{
  "12": {
    "class_type": "NSFWGrokFusionPro",
    "inputs": {
      "base_prompt": "",
      "strategy": "balanced",
      "tag_weight": 1.0,
      "preset": "None",
      "annotator": false,
      "second_prompt": "",
      "blend_weight": 0.5,
      "auto_cycle": false,
      "cycle_styles": ""
    }
  }
}
```

## Notes

- Behavior and defaults are defined in the node source file.
- If this node depends on an external API, provide credentials through node inputs or environment variables as required.
