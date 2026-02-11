# Prompt Merge

- Node ID: `PromptMergeNode`
- Class: `PromptMergeNode`
- Category: `babydjacNODES/Utils`
- Function: `process`
- Module: `babydjacNODES.Utils.PromptMergeNode`

## Purpose

Merges multiple tag lists with optional dedupe, case normalization, sorting, and truncation.

## Required Inputs

- `taglist_a`: `STRING` (default=''; multiline=True)
- `taglist_b`: `STRING` (default=''; multiline=True)

## Optional Inputs

- `extra_taglist`: `STRING` (default=''; multiline=True)
- `dedupe`: `BOOLEAN` (default=True)
- `lowercase`: `BOOLEAN` (default=False)
- `sort_alpha`: `BOOLEAN` (default=False)
- `max_tokens`: `INT` (default=0; min=0; max=10000; step=1)

## Outputs

- `merged`: `STRING`

## Minimal Usage

Set required inputs, then queue the workflow. Suggested starter values:

- `taglist_a` -> ``
- `taglist_b` -> ``

## Workflow Snippet

Minimal prompt JSON fragment (replace node ids/connections as needed):

```json
{
  "12": {
    "class_type": "PromptMergeNode",
    "inputs": {
      "taglist_a": "",
      "taglist_b": ""
    }
  }
}
```

## Notes

- Behavior and defaults are defined in the node source file.
- If this node depends on an external API, provide credentials through node inputs or environment variables as required.
