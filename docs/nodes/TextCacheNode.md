# Text Cache

- Node ID: `TextCacheNode`
- Class: `TextCacheNode`
- Category: `babydjacNODES/Utils`
- Function: `process`
- Module: `babydjacNODES.Utils.TextCacheNode`

## Purpose

Small key/value text cache node with get/set/delete operations.

## Required Inputs

- `mode`: `CHOICE` (default='get'; choices=['get', 'set', 'delete'])
- `key`: `STRING` (default=''; multiline=False)

## Optional Inputs

- `value`: `STRING` (default=''; multiline=True)
- `namespace`: `STRING` (default='default')

## Outputs

- `value`: `STRING`

## Minimal Usage

Set required inputs, then queue the workflow. Suggested starter values:

- `mode` -> `get`
- `key` -> ``

## Workflow Snippet

Minimal prompt JSON fragment (replace node ids/connections as needed):

```json
{
  "12": {
    "class_type": "TextCacheNode",
    "inputs": {
      "mode": "get",
      "key": ""
    }
  }
}
```

## Notes

- Behavior and defaults are defined in the node source file.
- If this node depends on an external API, provide credentials through node inputs or environment variables as required.
