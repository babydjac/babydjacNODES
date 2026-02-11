# Grok Flux Prompt Optimizer

- Node ID: `GrokFluxPromptOptimizer`
- Class: `GrokFluxPromptOptimizer`
- Category: `babydjacNODES/Analyze`
- Function: `optimize_prompt`
- Module: `babydjacNODES.Analyze.GrokFluxPromptOptimizer`

## Purpose

Optimizes an existing Flux prompt from image context and user edit instructions.

## Required Inputs

- `image`: `IMAGE`
- `user_instruction`: `STRING` (default='Make this image more vibrant and colorful'; multiline=True; placeholder='Describe what changes you want to make to the image...')
- `api_key`: `STRING` (default=''; placeholder='Enter your Grok API key')

## Optional Inputs

- `style_preference`: COMBO (`photorealistic, artistic, cinematic, portrait, landscape, abstract, anime, concept_art`) (default='photorealistic')
- `detail_level`: COMBO (`basic, detailed, very_detailed`) (default='detailed')

## Outputs

- `optimized_prompt`: `STRING`

## Minimal Usage

Set required inputs, then queue the workflow. Suggested starter values:

- `image` -> `<connect>`
- `user_instruction` -> `Make this image more vibrant and colorful`
- `api_key` -> ``

## Workflow Snippet

Minimal prompt JSON fragment (replace node ids/connections as needed):

```json
{
  "12": {
    "class_type": "GrokFluxPromptOptimizer",
    "inputs": {
      "image": "<connect>",
      "user_instruction": "Make this image more vibrant and colorful",
      "api_key": ""
    }
  }
}
```

## Notes

- Behavior and defaults are defined in the node source file.
- If this node depends on an external API, provide credentials through node inputs or environment variables as required.
