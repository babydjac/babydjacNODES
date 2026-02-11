# No-Repeat Picker

- Node ID: `NoRepeatPickerNode`
- Class: `NoRepeatPickerNode`
- Category: `babydjacNODES/Utils`
- Function: `process`
- Module: `babydjacNODES.Utils.NoRepeatPickerNode`

## Purpose

Selects items from a multiline list while persisting no-repeat history.

## Required Inputs

- `items_text`: `STRING` (default=''; multiline=True)

## Optional Inputs

- `randomize`: `BOOLEAN` (default=True)
- `item_index`: `INT` (default=0; min=0; max=1000000; step=1)
- `persist_key`: `STRING` (default='default')
- `reuse_last`: `BOOLEAN` (default=False)
- `reset_history`: `BOOLEAN` (default=False)

## Outputs

- `item`: `STRING`

## Minimal Usage

Set required inputs, then queue the workflow. Suggested starter values:

- `items_text` -> ``

## Workflow Snippet

Minimal prompt JSON fragment (replace node ids/connections as needed):

```json
{
  "12": {
    "class_type": "NoRepeatPickerNode",
    "inputs": {
      "items_text": ""
    }
  }
}
```

## Notes

- Behavior and defaults are defined in the node source file.
- If this node depends on an external API, provide credentials through node inputs or environment variables as required.
