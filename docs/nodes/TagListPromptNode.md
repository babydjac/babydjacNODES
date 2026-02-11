# Taglist Prompt

- Node ID: `TagListPromptNode`
- Class: `TagListPromptNode`
- Category: `babydjacNODES/Taglists`
- Function: `process`
- Module: `babydjacNODES.Taglists.TagListPromptNode`
- Output node: `True`

## Purpose

Direct tag list prompt node that inherits the SafeTagListPromptNode behavior.

## Required Inputs

- `template_text`: `STRING` (default=''; multiline=True)
- `custom_idea`: `STRING` (default=''; multiline=True)
- `api_key`: `STRING` (default='')

## Optional Inputs

- `model_name`: `STRING` (default='grok-3-latest')
- `temperature`: `FLOAT` (default=0.2; min=0.0; max=1.0; step=0.05)
- `safe_mode`: `BOOLEAN` (default=True)
- `blocklist`: `STRING` (default='nsfw, porn, sexual, sex, nude, naked, topless, boobs, breast, areola, pussy, ass, butt, buttocks, erotic, explicit, horny, aroused, arousing, cum, ejaculate, semen, oral, anal, penetration, blowjob, handjob, vagina, penis, cock, dick, fetish, bdsm'; multiline=True)

## Outputs

- `taglist_prompt`: `STRING`

## Minimal Usage

Set required inputs, then queue the workflow. Suggested starter values:

- `template_text` -> ``
- `custom_idea` -> ``
- `api_key` -> ``

## Workflow Snippet

Minimal prompt JSON fragment (replace node ids/connections as needed):

```json
{
  "12": {
    "class_type": "TagListPromptNode",
    "inputs": {
      "template_text": "",
      "custom_idea": "",
      "api_key": ""
    }
  }
}
```

## Notes

- Behavior and defaults are defined in the node source file.
- If this node depends on an external API, provide credentials through node inputs or environment variables as required.
