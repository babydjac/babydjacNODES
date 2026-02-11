# NSFW Grok → Pro-Level Prompt

- Node ID: `NSFWGrokDescriberPro`
- Class: `NSFWGrokDescriberPro`
- Category: `babydjacNODES/Analyze`
- Function: `process`
- Module: `babydjacNODES.Analyze.NSFWGrokDescriberPro`

## Purpose

Returns expanded descriptive prompt outputs from an image and instruction set.

## Required Inputs

- `image`: `IMAGE`
- `api_key`: `STRING` (default=''; multiline=False)
- `prepend_text`: `STRING` (default=''; multiline=True)
- `append_text`: `STRING` (default=''; multiline=True)
- `score_strategy`: COMBO (`ascending, descending, manual`)
- `debug_output`: COMBO (`disable, enable`)

## Outputs

- `description`: `STRING`
- `positive_prompt`: `STRING`
- `negative_prompt`: `STRING`

## Minimal Usage

Set required inputs, then queue the workflow. Suggested starter values:

- `image` -> `<connect>`
- `api_key` -> ``
- `prepend_text` -> ``
- `append_text` -> ``
- `score_strategy` -> `ascending`
- `debug_output` -> `disable`

## Workflow Snippet

Minimal prompt JSON fragment (replace node ids/connections as needed):

```json
{
  "12": {
    "class_type": "NSFWGrokDescriberPro",
    "inputs": {
      "image": "<connect>",
      "api_key": "",
      "prepend_text": "",
      "append_text": "",
      "score_strategy": "ascending",
      "debug_output": "disable"
    }
  }
}
```

## Notes

- Behavior and defaults are defined in the node source file.
- If this node depends on an external API, provide credentials through node inputs or environment variables as required.
