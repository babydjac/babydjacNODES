# Z-Image Turbo Prompt Engineer

- Node ID: `ZImageTurboPromptEngineer`
- Class: `ZImageTurboPromptEngineer`
- Category: `babydjacNODES/Prompting/Z-Image`
- Function: `process`
- Module: `babydjacNODES.Prompting.Z_Image.ZImageTurboPromptEngineer`

## Purpose

Fast prompt builder for Z-Image Turbo workflows with simplified controls.

## Required Inputs

- `text_input`: `STRING` (multiline=True; placeholder="Enter your concept (e.g., 'cyberpunk street racer')..."; dynamicPrompts=True)
- `style`: COMBO (`None, Ultra-sharp hyperrealism, Fashion editorial (e.g., Vogue-style), Cinematic color grading, IMAX film realism, Photojournalistic documentary style, Macro realism, Annie Leibovitz lighting style, Medium format digital look, HDR tonality without over-processing, Fine art gallery portrait style`) (default='Photorealistic')
- `camera`: COMBO (`None, Shot on a Canon EOS R5, Captured with a Sony A1, Nikon Z9 full-frame sensor, Medium format Fujifilm GFX100 II, Leica SL2 Summilux lens, 8K RAW photo, 85mm f/1.2 lens sharpness, Zeiss Otus lens detail, Shallow depth of field (DoF), Super-resolution DSLR quality`) (default='None')
- `lighting`: COMBO (`None, Rembrandt lighting, Softbox key light with rim light, Golden hour lighting, Overcast diffused lighting, Harsh hard-light shadows (film noir style), Godox AD600 strobe flash look, Studio lighting with hair light, Reflective fill light (silver reflector), Ring light catchlights, LED panel ambient light`) (default='None')
- `framing`: COMBO (`None, Rule of thirds composition, Portrait shot, eye-level, Cinematic wide-angle shot, Close-up with bokeh background, Dutch angle (tilted perspective), Over-the-shoulder framing, Centered symmetrical shot, Negative space composition, Top-down flat lay, Environmental portrait`) (default='None')
- `quality_preset`: COMBO (`Speed, Balanced, Max Quality`) (default='Balanced')

## Optional Inputs

- `grok_api_key`: `STRING` (default=''; multiline=False; placeholder='xai-...')
- `grok_model`: COMBO (`grok-4-1-fast-reasoning, grok-4-1-fast-non-reasoning, grok-code-fast-1, grok-4-fast-reasoning, grok-4-fast-non-reasoning, grok-4-0709, grok-3-mini, grok-3, grok-2-vision-1212, grok-imagine-image-pro, grok-imagine-image, grok-2-image-1212, grok-imagine-video, grok-2-vision-latest, grok-3-latest, grok-beta, grok-4`) (default='grok-2-vision-1212')
- `reference_image`: `IMAGE`

## Hidden Inputs

- `unique_id`: `UNIQUE_ID`
- `extra_pnginfo`: `EXTRA_PNGINFO`

## Outputs

- `optimized_prompt`: `STRING`
- `cfg`: `FLOAT`
- `steps`: `INT`
- `status_info`: `STRING`
- `expert_breakdown`: `STRING`

## Minimal Usage

Set required inputs, then queue the workflow. Suggested starter values:

- `text_input` -> ``
- `style` -> `Photorealistic`
- `camera` -> `None`
- `lighting` -> `None`
- `framing` -> `None`
- `quality_preset` -> `Balanced`

## Workflow Snippet

Minimal prompt JSON fragment (replace node ids/connections as needed):

```json
{
  "12": {
    "class_type": "ZImageTurboPromptEngineer",
    "inputs": {
      "text_input": "",
      "style": "Photorealistic",
      "camera": "None",
      "lighting": "None",
      "framing": "None",
      "quality_preset": "Balanced"
    }
  }
}
```

## Notes

- Behavior and defaults are defined in the node source file.
- If this node depends on an external API, provide credentials through node inputs or environment variables as required.
