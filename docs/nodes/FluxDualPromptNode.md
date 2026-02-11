# Flux Dual Prompt Node (Grok)

- Node ID: `FluxDualPromptNode`
- Class: `FluxDualPromptNode`
- Category: `babydjacNODES/Prompting/Flux`
- Function: `generate_prompts`
- Module: `babydjacNODES.Prompting.Flux.FluxDualPromptNode`

## Purpose

Calls Grok to produce dual Flux prompts (short CLIP-style + long descriptive prompt).

## Required Inputs

- `api_key`: `STRING` (default=''; multiline=False)
- `idea`: `STRING` (default='A short description of the scene or concept'; multiline=True)
- `model`: `STRING` (default='grok-3-latest')
- `temperature`: `FLOAT` (default=0.7; min=0.0; max=2.0; step=0.1)

## Outputs

- `output_0`: `STRING`
- `output_1`: `STRING`

## Minimal Usage

Set required inputs, then queue the workflow. Suggested starter values:

- `api_key` -> ``
- `idea` -> `A short description of the scene or concept`
- `model` -> `grok-3-latest`
- `temperature` -> `0.7`

## Workflow Snippet

Minimal prompt JSON fragment (replace node ids/connections as needed):

```json
{
  "12": {
    "class_type": "FluxDualPromptNode",
    "inputs": {
      "api_key": "",
      "idea": "A short description of the scene or concept",
      "model": "grok-3-latest",
      "temperature": 0.7
    }
  }
}
```

## Notes

- Behavior and defaults are defined in the node source file.
- If this node depends on an external API, provide credentials through node inputs or environment variables as required.
