# Latent Size Controller

- Node ID: `InteractiveEmptyLatent`
- Class: `InteractiveEmptyLatent`
- Category: `babydjacNODES/Latents/Interactive`
- Function: `generate`
- Module: `babydjacNODES.Latents.InteractiveEmptyLatent`

## Purpose

Creates an empty latent with interactive resolution controls (graph/histogram UI + model-aware presets).

## Required Inputs

- `width`: `INT` (default=1024; min=64; max=2048; step=8)
- `height`: `INT` (default=1024; min=64; max=2048; step=8)
- `batch_size`: `INT` (default=1; min=1; max=16)
- `model_profile`: COMBO (`WAN 2.1 / WAN 2.2, SD 1.5, SDXL, Z-Image / Z-Image Turbo`) (default='SDXL')
- `snap_to`: COMBO (`auto, 8, 16, 32, 64`) (default='auto')
- `ui_mode`: COMBO (`graph, histogram`) (default='graph')
- `aspect_lock`: `BOOLEAN` (default=False)
- `preset`: COMBO (`custom, Low VRAM (480x480), Portrait Detail (480x832), Mid Detail (720x1280), High Detail (1536x1536), Base (512x512), High Quality (768x768), Landscape (768x512), Portrait (512x768), Wide (896x512), Tall (512x896), Base (1024x1024), Portrait (896x1152), Landscape (1152x896), Tall Portrait (768x1344), Wide Landscape (1344x768), Tall (768x1152), Horizontal (1152x768), Ultra Fast (512x512), Fast Square (720x720), Balanced Vertical (720x1280), Balanced Square (1024x1024), High Quality (1344x1344)`) (default='custom')

## Outputs

- `latent`: `LATENT`

## Minimal Usage

Set required inputs, then queue the workflow. Suggested starter values:

- `width` -> `1024`
- `height` -> `1024`
- `batch_size` -> `1`
- `model_profile` -> `SDXL`
- `snap_to` -> `auto`
- `ui_mode` -> `graph`
- `aspect_lock` -> `False`
- `preset` -> `custom`

## Workflow Snippet

Minimal prompt JSON fragment (replace node ids/connections as needed):

```json
{
  "12": {
    "class_type": "InteractiveEmptyLatent",
    "inputs": {
      "width": 1024,
      "height": 1024,
      "batch_size": 1,
      "model_profile": "SDXL",
      "snap_to": "auto",
      "ui_mode": "graph",
      "aspect_lock": false,
      "preset": "custom"
    }
  }
}
```

## Notes

- Behavior and defaults are defined in the node source file.
- If this node depends on an external API, provide credentials through node inputs or environment variables as required.
