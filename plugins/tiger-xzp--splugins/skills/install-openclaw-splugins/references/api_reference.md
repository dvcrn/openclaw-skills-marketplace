# Example Reference Documentation

This is an example reference file for the hello-world-demo skill.

Reference files are used when you have detailed documentation that:
1. Is too long to fit in the main SKILL.md
2. Is only needed for specific use cases
3. Doesn't need to be loaded into context every time the skill is used

OpenClaw will only load this reference file when it's explicitly needed, which saves context space.

## Example Reference Content

Here's an example of what a simple API reference might look like:

### Hello World API

**Endpoint:** `GET /api/hello`

**Description:** Returns a hello world message

**Parameters:**
- `name` (optional): Name to greet, defaults to "World"

**Example Request:**
```
GET /api/hello?name=OpenClaw
```

**Example Response:**
```json
{
  "message": "Hello, OpenClaw!",
  "success": true
}
```

**Status Codes:**
- `200 OK`: Request succeeded
- `400 Bad Request`: Invalid parameter
- `500 Internal Server Error`: Server error

## Why Use References?

By putting this detailed content in a reference file instead of SKILL.md:
- We keep SKILL.md small and focused on the core workflow
- Context is only used when this reference is actually needed
- We can include more detailed information without bloating the main skill entry

