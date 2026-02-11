# Flux Prompt Builder

- Node ID: `FluxPromptBuilder`
- Class: `FluxPromptBuilder`
- Category: `babydjacNODES/Prompting/Flux`
- Function: `generate`
- Module: `babydjacNODES.Prompting.Flux.FluxPromptBuilder`

## Purpose

Constructs Flux-ready positive and negative prompts using local templates and safety controls.

## Required Inputs

- `subject`: `STRING` (default='vague subject (e.g., portrait in studio)')
- `style`: COMBO (`cinematic, glamour, artistic nude, editorial, film still, photoreal, analog`)
- `camera`: COMBO (`35mm, 50mm, 85mm, macro, telephoto`)
- `lighting`: COMBO (`softbox, rembrandt, split, rim, golden hour, hdr studio`)
- `spice`: `FLOAT` (default=0.35; min=0.0; max=1.0; step=0.01)
- `safety_level`: COMBO (`cautious, standard, raw`)
- `use_grok`: `BOOLEAN` (default=False)

## Optional Inputs

- `grok_api_key`: `STRING` (default=''; multiline=False; placeholder='sk-...')
- `guidance_tags`: `STRING` (default='')
- `forbidden_tags`: `STRING` (default='lowres, blurry, watermark')
- `prompt_override`: `STRING` (default='')
- `use_canvas_ui`: `BOOLEAN` (default=False)

## Hidden Inputs

- `unique_id`: `UNIQUE_ID`
- `prompt`: `PROMPT`

## Outputs

- `positive`: `STRING`
- `negative`: `STRING`

## Minimal Usage

Set required inputs, then queue the workflow. Suggested starter values:

- `subject` -> `vague subject (e.g., portrait in studio)`
- `style` -> `cinematic`
- `camera` -> `35mm`
- `lighting` -> `softbox`
- `spice` -> `0.35`
- `safety_level` -> `cautious`
- `use_grok` -> `False`

## Workflow Snippet

Minimal prompt JSON fragment (replace node ids/connections as needed):

```json
{
  "12": {
    "class_type": "FluxPromptBuilder",
    "inputs": {
      "subject": "vague subject (e.g., portrait in studio)",
      "style": "cinematic",
      "camera": "35mm",
      "lighting": "softbox",
      "spice": 0.35,
      "safety_level": "cautious",
      "use_grok": false
    }
  }
}
```

## Notes

- Behavior and defaults are defined in the node source file.
- If this node depends on an external API, provide credentials through node inputs or environment variables as required.
