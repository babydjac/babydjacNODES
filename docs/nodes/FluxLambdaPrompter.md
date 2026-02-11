# Flux Lambda Prompter

- Node ID: `FluxLambdaPrompter`
- Class: `FluxLambdaPrompter`
- Category: `babydjacNODES/Prompting/Flux`
- Function: `generate_prompt`
- Module: `babydjacNODES.Prompting.Flux.FluxLambdaPrompter`

## Purpose

Uses a Lambda-hosted model endpoint to generate refined Flux prompt pairs.

## Required Inputs

- `api_key`: `STRING` (default=''; multiline=False)
- `subject_scene`: `STRING` (default='A playful kitten with yarn balls'; multiline=True)
- `model`: `STRING` (default='llama-4-maverick-17b-128e-instruct-fp8')
- `temperature`: `FLOAT` (default=0.9; min=0.0; max=1.5; step=0.1)

## Outputs

- `output_0`: `STRING`
- `output_1`: `STRING`

## Minimal Usage

Set required inputs, then queue the workflow. Suggested starter values:

- `api_key` -> ``
- `subject_scene` -> `A playful kitten with yarn balls`
- `model` -> `llama-4-maverick-17b-128e-instruct-fp8`
- `temperature` -> `0.9`

## Workflow Snippet

Minimal prompt JSON fragment (replace node ids/connections as needed):

```json
{
  "12": {
    "class_type": "FluxLambdaPrompter",
    "inputs": {
      "api_key": "",
      "subject_scene": "A playful kitten with yarn balls",
      "model": "llama-4-maverick-17b-128e-instruct-fp8",
      "temperature": 0.9
    }
  }
}
```

## Notes

- Behavior and defaults are defined in the node source file.
- If this node depends on an external API, provide credentials through node inputs or environment variables as required.
