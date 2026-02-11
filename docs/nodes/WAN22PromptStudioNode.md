# WAN 2.2 Prompt Studio

- Node ID: `WAN22PromptStudioNode`
- Class: `WAN22PromptStudioNode`
- Category: `babydjacNODES/Prompting/WAN-2.2`
- Function: `generate_expert_prompt`
- Module: `babydjacNODES.Prompting.WAN_2_2.WAN22PromptStudioNode`

## Purpose

Generates WAN 2.2 oriented prompt sets for video/image workflows.

## Required Inputs

- `user_idea`: `STRING` (default=''; multiline=True)
- `grok_model`: COMBO (`grok-4-1-fast-reasoning, grok-4-1-fast-non-reasoning, grok-code-fast-1, grok-4-fast-reasoning, grok-4-fast-non-reasoning, grok-4-0709, grok-3-mini, grok-3, grok-2-vision-1212, grok-imagine-image-pro, grok-imagine-image, grok-2-image-1212, grok-imagine-video, grok-2-vision-latest, grok-3-latest, grok-beta, grok-4`) (default='grok-2-vision-1212')
- `content_mode`: COMBO (`SFW, NSFW`) (default='SFW')
- `prompt_complexity`: COMBO (`Basic, Advanced, Cinematic Pro`) (default='Advanced')
- `style_preference`: COMBO (`Realistic, Cinematic, Artistic, Documentary, Experimental, Pornographic`) (default='Cinematic')
- `motion_intensity`: COMBO (`Subtle, Moderate, Dynamic, Extreme`) (default='Moderate')
- `camera_style`: COMBO (`Static, Smooth Movement, Dynamic Tracking, Experimental`) (default='Smooth Movement')
- `lighting_mood`: COMBO (`Natural, Dramatic, Soft, High Contrast, Atmospheric`) (default='Natural')
- `color_palette`: COMBO (`Warm, Cool, Neutral, Saturated, Desaturated`) (default='Neutral')
- `shot_type`: COMBO (`Close-up, Medium, Wide, Extreme Wide, Mixed`) (default='Medium')
- `time_of_day`: COMBO (`Auto, Sunrise, Day, Sunset, Dusk, Night, Dawn`) (default='Auto')
- `temperature`: `FLOAT` (default=0.7; min=0.0; max=1.5; step=0.1)

## Optional Inputs

- `api_key`: `STRING` (forceInput=True)
- `specific_subject`: `STRING` (default=''; multiline=False)
- `environment`: `STRING` (default=''; multiline=False)
- `mood_keywords`: `STRING` (default=''; multiline=False)
- `technical_specs`: `STRING` (default=''; multiline=False)
- `reference_image`: `IMAGE`

## Outputs

- `wan22_prompt`: `STRING`
- `prompt_breakdown`: `STRING`
- `technical_notes`: `STRING`

## Minimal Usage

Set required inputs, then queue the workflow. Suggested starter values:

- `user_idea` -> ``
- `grok_model` -> `grok-2-vision-1212`
- `content_mode` -> `SFW`
- `prompt_complexity` -> `Advanced`
- `style_preference` -> `Cinematic`
- `motion_intensity` -> `Moderate`
- `camera_style` -> `Smooth Movement`
- `lighting_mood` -> `Natural`
- `color_palette` -> `Neutral`
- `shot_type` -> `Medium`
- `time_of_day` -> `Auto`
- `temperature` -> `0.7`

## Workflow Snippet

Minimal prompt JSON fragment (replace node ids/connections as needed):

```json
{
  "12": {
    "class_type": "WAN22PromptStudioNode",
    "inputs": {
      "user_idea": "",
      "grok_model": "grok-2-vision-1212",
      "content_mode": "SFW",
      "prompt_complexity": "Advanced",
      "style_preference": "Cinematic",
      "motion_intensity": "Moderate",
      "camera_style": "Smooth Movement",
      "lighting_mood": "Natural",
      "color_palette": "Neutral",
      "shot_type": "Medium",
      "time_of_day": "Auto",
      "temperature": 0.7
    }
  }
}
```

## Notes

- Behavior and defaults are defined in the node source file.
- If this node depends on an external API, provide credentials through node inputs or environment variables as required.
