# Weight Adjust

- Node ID: `WeightAdjustNode`
- Class: `WeightAdjustNode`
- Category: `babydjacNODES/Utils`
- Function: `process`
- Module: `babydjacNODES.Utils.WeightAdjustNode`

## Purpose

Applies weight scaling rules across weighted and unweighted prompt tags.

## Required Inputs

- `taglist`: `STRING` (default=''; multiline=True)

## Optional Inputs

- `multiply`: `FLOAT` (default=1.0; min=0.0; max=10.0; step=0.05)
- `base_weight`: `FLOAT` (default=1.1; min=0.0; max=10.0; step=0.05)
- `apply_to_unweighted`: `BOOLEAN` (default=True)
- `clamp_min`: `FLOAT` (default=0.1)
- `clamp_max`: `FLOAT` (default=2.0)
- `round_to`: `INT` (default=2; min=0; max=6; step=1)

## Outputs

- `adjusted`: `STRING`

## Minimal Usage

Set required inputs, then queue the workflow. Suggested starter values:

- `taglist` -> ``

## Workflow Snippet

Minimal prompt JSON fragment (replace node ids/connections as needed):

```json
{
  "12": {
    "class_type": "WeightAdjustNode",
    "inputs": {
      "taglist": ""
    }
  }
}
```

## Notes

- Behavior and defaults are defined in the node source file.
- If this node depends on an external API, provide credentials through node inputs or environment variables as required.
