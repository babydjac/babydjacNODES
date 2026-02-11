# Qwen Image Prompter

- Node ID: `QwenImagePrompter`
- Class: `QwenImagePrompter`
- Category: `babydjacNODES/Prompting`
- Function: `generate_prompt`
- Module: `babydjacNODES.Prompting.QwenImagePrompter`
- Output node: `True`

## Purpose

Generates image prompts using a Qwen-style prompt strategy and formatting.

## Required Inputs

- `idea`: `STRING` (default=''; multiline=True)
- `api_key`: `STRING` (default='')

## Outputs

- `qwen_prompt`: `STRING`

## Minimal Usage

Set required inputs, then queue the workflow. Suggested starter values:

- `idea` -> ``
- `api_key` -> ``

## Workflow Snippet

Minimal prompt JSON fragment (replace node ids/connections as needed):

```json
{
  "12": {
    "class_type": "QwenImagePrompter",
    "inputs": {
      "idea": "",
      "api_key": ""
    }
  }
}
```

## Notes

- Behavior and defaults are defined in the node source file.
- If this node depends on an external API, provide credentials through node inputs or environment variables as required.
