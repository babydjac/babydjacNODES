# Prompt Rotator (Dynamic Batch)

- Node ID: `DynamicPromptBatcher`
- Class: `DynamicPromptBatcher`
- Category: `babydjacNODES/Utils/Batching`
- Function: `collect`
- Module: `babydjacNODES.Utils.DynamicPromptBatcher`

## Purpose

Collects prompt inputs into a list output for batched or rotating workflows.

## Required Inputs

- `prompt_1`: `STRING` (default=''; multiline=True)

## Outputs

- `prompts`: `STRING`

## Minimal Usage

Set required inputs, then queue the workflow. Suggested starter values:

- `prompt_1` -> ``

## Workflow Snippet

Minimal prompt JSON fragment (replace node ids/connections as needed):

```json
{
  "12": {
    "class_type": "DynamicPromptBatcher",
    "inputs": {
      "prompt_1": ""
    }
  }
}
```

## Notes

- Behavior and defaults are defined in the node source file.
- If this node depends on an external API, provide credentials through node inputs or environment variables as required.
