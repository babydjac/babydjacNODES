# Flux Lifestyle Prompt Node

- Node ID: `FluxLifestylePromptNode`
- Class: `FluxLifestylePromptNode`
- Category: `babydjacNODES/Prompting/Flux`
- Function: `generate_prompt`
- Module: `babydjacNODES.Prompting.Flux.FluxLifestylePromptNode`
- Output node: `True`

## Purpose

Enhances lifestyle photo prompts through Grok for Flux-focused generation.

## Required Inputs

- `prompt`: `STRING` (default=''; multiline=True)
- `api_key`: `STRING` (default='')

## Outputs

- `enhanced_prompt`: `STRING`

## Minimal Usage

Set required inputs, then queue the workflow. Suggested starter values:

- `prompt` -> ``
- `api_key` -> ``

## Workflow Snippet

Minimal prompt JSON fragment (replace node ids/connections as needed):

```json
{
  "12": {
    "class_type": "FluxLifestylePromptNode",
    "inputs": {
      "prompt": "",
      "api_key": ""
    }
  }
}
```

## Notes

- Behavior and defaults are defined in the node source file.
- If this node depends on an external API, provide credentials through node inputs or environment variables as required.
