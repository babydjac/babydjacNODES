# Taglist Sanitizer

- Node ID: `TaglistSanitizerNode`
- Class: `TaglistSanitizerNode`
- Category: `babydjacNODES/Utils`
- Function: `process`
- Module: `babydjacNODES.Utils.TaglistSanitizerNode`

## Purpose

Sanitizes tag lists (dedupe, lowercase, strip weights, sort).

## Required Inputs

- `taglist`: `STRING` (default=''; multiline=True)

## Optional Inputs

- `dedupe`: `BOOLEAN` (default=True)
- `lowercase`: `BOOLEAN` (default=False)
- `strip_weights`: `BOOLEAN` (default=False)
- `sort_alpha`: `BOOLEAN` (default=False)

## Outputs

- `sanitized`: `STRING`

## Minimal Usage

Set required inputs, then queue the workflow. Suggested starter values:

- `taglist` -> ``

## Workflow Snippet

Minimal prompt JSON fragment (replace node ids/connections as needed):

```json
{
  "12": {
    "class_type": "TaglistSanitizerNode",
    "inputs": {
      "taglist": ""
    }
  }
}
```

## Notes

- Behavior and defaults are defined in the node source file.
- If this node depends on an external API, provide credentials through node inputs or environment variables as required.
