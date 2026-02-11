# Grok PonyXL Prompter

- Node ID: `GrokPonyXLPrompter`
- Class: `GrokPonyXLPrompter`
- Category: `babydjacNODES/Prompting/PonyXL`
- Function: `generate`
- Module: `babydjacNODES.Prompting.PonyXL.GrokPonyXLPrompter`

## Purpose

Analyzes an input image with Grok Vision and returns PonyXL-style prompt/negative tags.

## Required Inputs

- `image`: `IMAGE`

## Optional Inputs

- `api_key`: `STRING` (default=''; multiline=False)
- `base_url`: `STRING` (default='https://api.x.ai/v1'; multiline=False)
- `exaggeration`: `INT` (default=5; min=0; max=10; step=1)
- `add_realism_tags`: `BOOLEAN` (default=True)
- `quality_boost`: `BOOLEAN` (default=True)
- `custom_negatives`: `STRING` (default=''; multiline=True)
- `extra_tags`: `STRING` (default=''; multiline=True)
- `instruction`: `STRING` (default=''; multiline=True)
- `max_tokens`: `INT` (default=256; min=32; max=1024)
- `temperature`: `FLOAT` (default=0.45; min=0.0; max=1.0; step=0.05)
- `top_p`: `FLOAT` (default=0.9; min=0.1; max=1.0; step=0.05)
- `frequency_penalty`: `FLOAT` (default=0.2; min=0.0; max=2.0; step=0.1)
- `presence_penalty`: `FLOAT` (default=0.0; min=0.0; max=2.0; step=0.1)
- `shuffle_order`: `BOOLEAN` (default=True)

## Outputs

- `prompt`: `STRING`
- `negative`: `STRING`

## Minimal Usage

Set required inputs, then queue the workflow. Suggested starter values:

- `image` -> `<connect>`

## Workflow Snippet

Minimal prompt JSON fragment (replace node ids/connections as needed):

```json
{
  "12": {
    "class_type": "GrokPonyXLPrompter",
    "inputs": {
      "image": "<connect>"
    }
  }
}
```

## Notes

- Behavior and defaults are defined in the node source file.
- If this node depends on an external API, provide credentials through node inputs or environment variables as required.
