# HTTP JSON

- Node ID: `HTTPJsonNode`
- Class: `HTTPJsonNode`
- Category: `babydjacNODES/Utils`
- Function: `process`
- Module: `babydjacNODES.Utils.HTTPJsonNode`

## Purpose

Makes HTTP requests and returns response text for API-backed workflows.

## Required Inputs

- `url`: `STRING` (default=''; multiline=False)

## Optional Inputs

- `method`: `CHOICE` (default='GET'; choices=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
- `headers_json`: `STRING` (default='{}'; multiline=True)
- `body`: `STRING` (default=''; multiline=True)
- `timeout_sec`: `INT` (default=30; min=1; max=300; step=1)

## Outputs

- `response_text`: `STRING`

## Minimal Usage

Set required inputs, then queue the workflow. Suggested starter values:

- `url` -> ``

## Workflow Snippet

Minimal prompt JSON fragment (replace node ids/connections as needed):

```json
{
  "12": {
    "class_type": "HTTPJsonNode",
    "inputs": {
      "url": ""
    }
  }
}
```

## Notes

- Behavior and defaults are defined in the node source file.
- If this node depends on an external API, provide credentials through node inputs or environment variables as required.
