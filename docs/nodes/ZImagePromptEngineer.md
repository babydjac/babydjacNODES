# Z-Image Prompt Engineer

- Node ID: `ZImagePromptEngineer`
- Class: `ZImagePromptEngineer`
- Category: `babydjacNODES/Prompting/Z-Image`
- Function: `process`
- Module: `babydjacNODES.Prompting.Z_Image.ZImagePromptEngineer`

## Purpose

Builds a structured Z-Image prompt with positive/negative text and generation settings.

## Required Inputs

- `text_input`: `STRING` (multiline=True; placeholder="Describe the concept (e.g., 'storm-lit alpine cabin at dawn')..."; dynamicPrompts=True)
- `prompt_length`: COMBO (`Lean, Standard, Rich, Ultra`) (default='Standard')
- `style`: COMBO (`None, Photorealistic, Cinematic, Documentary, Fashion editorial, Fine art portrait, Architectural, Product photography, Macro realism, Illustrative realism, Oil painting, Watercolor, 3D render, Film still, Vintage analog, Minimalist design, High contrast`) (default='Photorealistic')
- `camera`: COMBO (`None, Canon EOS R5, Sony A1, Nikon Z9, Fujifilm GFX100 II, Leica SL2, 35mm film look, 85mm f/1.4 lens, 24mm wide angle, 50mm standard lens, Tilt-shift`) (default='None')
- `lighting`: COMBO (`None, Soft window light, Golden hour, Overcast, Studio softbox, Rim light, Noir hard light, Cinematic top light, Neon practicals, Candlelight`) (default='None')
- `framing`: COMBO (`None, Close-up, Medium shot, Full body, Wide establishing, Rule of thirds, Centered symmetry, Over-the-shoulder, Top-down, Low angle, High angle`) (default='None')
- `mood`: COMBO (`None, Calm, Tense, Hopeful, Melancholic, Joyful, Mysterious, Luxurious, Gritty, Serene`) (default='None')
- `color_palette`: COMBO (`None, Warm earth tones, Cool muted, Monochrome, Vibrant pop, Desaturated, High key, Low key`) (default='None')
- `detail_focus`: COMBO (`None, Skin texture, Material realism, Architecture lines, Depth of field, Micro detail, Motion cues`) (default='None')
- `negative_focus`: COMBO (`None, Artifacts, Anatomy, Text/Watermark, Clutter, All`) (default='Artifacts')
- `quality_preset`: COMBO (`Fast Draft, Production, Max Quality, Exploration`) (default='Production')

## Optional Inputs

- `must_include`: `STRING` (default=''; multiline=True; placeholder='Hard requirements or specific details...')
- `avoid`: `STRING` (default=''; multiline=True; placeholder='Things to avoid in the image...')
- `grok_api_key`: `STRING` (default=''; multiline=False; placeholder='xai-...')
- `grok_model`: COMBO (`grok-4-1-fast-reasoning, grok-4-1-fast-non-reasoning, grok-code-fast-1, grok-4-fast-reasoning, grok-4-fast-non-reasoning, grok-4-0709, grok-3-mini, grok-3, grok-2-vision-1212, grok-imagine-image-pro, grok-imagine-image, grok-2-image-1212, grok-imagine-video, grok-2-vision-latest, grok-3-latest, grok-beta, grok-4`) (default='grok-2-vision-1212')
- `reference_image`: `IMAGE`

## Hidden Inputs

- `unique_id`: `UNIQUE_ID`
- `extra_pnginfo`: `EXTRA_PNGINFO`

## Outputs

- `positive_prompt`: `STRING`
- `negative_prompt`: `STRING`
- `cfg`: `FLOAT`
- `steps`: `INT`
- `status_info`: `STRING`
- `expert_breakdown`: `STRING`

## Minimal Usage

Set required inputs, then queue the workflow. Suggested starter values:

- `text_input` -> ``
- `prompt_length` -> `Standard`
- `style` -> `Photorealistic`
- `camera` -> `None`
- `lighting` -> `None`
- `framing` -> `None`
- `mood` -> `None`
- `color_palette` -> `None`
- `detail_focus` -> `None`
- `negative_focus` -> `Artifacts`
- `quality_preset` -> `Production`

## Workflow Snippet

Minimal prompt JSON fragment (replace node ids/connections as needed):

```json
{
  "12": {
    "class_type": "ZImagePromptEngineer",
    "inputs": {
      "text_input": "",
      "prompt_length": "Standard",
      "style": "Photorealistic",
      "camera": "None",
      "lighting": "None",
      "framing": "None",
      "mood": "None",
      "color_palette": "None",
      "detail_focus": "None",
      "negative_focus": "Artifacts",
      "quality_preset": "Production"
    }
  }
}
```

## Notes

- Behavior and defaults are defined in the node source file.
- If this node depends on an external API, provide credentials through node inputs or environment variables as required.
