# NSFW Grok to PonyXL

- Node ID: `NSFWGrokToPonyXL`
- Class: `NSFWGrokToPonyXL`
- Category: `babydjacNODES/Prompting/PonyXL`
- Function: `generate_prompts`
- Module: `babydjacNODES.Prompting.PonyXL.NSFWGrokToPonyXL`
- Output node: `True`

## Purpose

Transforms freeform prompt text into PonyXL-friendly positive/negative/tag outputs.

## Required Inputs

- `description`: `STRING` (default=''; multiline=True)
- `api_key`: `STRING` (default='')
- `motion_type`: `STRING` (default='hair swaying slightly')

## Outputs

- `ponyxl_prompt`: `STRING`
- `wan_prompt`: `STRING`
- `negative_prompt`: `STRING`

## Minimal Usage

Set required inputs, then queue the workflow. Suggested starter values:

- `description` -> ``
- `api_key` -> ``
- `motion_type` -> `hair swaying slightly`

## Workflow Snippet

Minimal prompt JSON fragment (replace node ids/connections as needed):

```json
{
  "12": {
    "class_type": "NSFWGrokToPonyXL",
    "inputs": {
      "description": "",
      "api_key": "",
      "motion_type": "hair swaying slightly"
    }
  }
}
```

## Notes

- Behavior and defaults are defined in the node source file.
- If this node depends on an external API, provide credentials through node inputs or environment variables as required.
