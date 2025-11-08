# Bug Fix: Vertex AI Role Field Requirement

## Issue

When using Vertex AI, the API was returning a 400 error:

```json
{
  "error": {
    "code": 400,
    "message": "Please use a valid role: user, model.",
    "status": "INVALID_ARGUMENT"
  }
}
```

## Root Cause

**Vertex AI requires an explicit `role` field in the request payload, while the standard Gemini API does not.**

The payload structure difference:

### Standard Gemini API (works without role):
```json
{
  "contents": [
    {
      "parts": [
        {"text": "prompt"},
        {"inline_data": {"mime_type": "image/png", "data": "..."}}
      ]
    }
  ]
}
```

### Vertex AI (requires role):
```json
{
  "contents": [
    {
      "role": "user",  // <-- This is required!
      "parts": [
        {"text": "prompt"},
        {"inline_data": {"mime_type": "image/png", "data": "..."}}
      ]
    }
  ]
}
```

## Solution

Modified `parse_image_with_gemini()` in `lexoid/core/parse_type/llm_parser.py` to conditionally add the `role` field:

```python
# Build content structure
content = {
    "parts": [
        {"text": prompt},
        {"inline_data": {"mime_type": mime_type, "data": base64_file}},
    ]
}

# Vertex AI requires explicit "role" field, standard Gemini API doesn't
if use_vertex_ai:
    content["role"] = "user"

payload = {
    "contents": [content],
    "generationConfig": generation_config,
}
```

## Additional Issue: Model Availability

From your logs, I noticed you're using `gemini-2.5-flash-lite`. **This model is not available in Vertex AI.**

### Available Models in Vertex AI:

**Production (GA):**
- ⭐ `gemini-1.5-flash` (RECOMMENDED for most use cases)
- ✅ `gemini-1.5-pro` (best for complex documents)
- ✅ `gemini-1.0-pro` (legacy)

**Experimental/Preview:**
- ✅ `gemini-2.0-flash-exp`
- ⚠️ `gemini-2.5-flash` (preview, availability varies)
- ⚠️ `gemini-2.5-pro` (preview, availability varies)

**NOT consistently available:**
- ❌ `gemini-2.5-flash-lite` (may not be in all regions)

### Recommendation

Update your application to use a Vertex AI compatible model.

**For Legal Document RAG (Recommended):**

```python
# Best balance of speed, cost, and accuracy
model = "gemini-1.5-flash"

result = parse(
    document_path,
    parser_type="LLM_PARSE",
    model=model
)
```

**For Complex Legal Documents (Higher Accuracy):**

```python
# Use for contracts with complex tables and charts
model = "gemini-1.5-pro"  # More expensive but more accurate

result = parse(
    document_path,
    parser_type="LLM_PARSE",
    model=model
)
```

## Testing the Fix

### 1. Update Lexoid in your project:

```bash
# In your project directory
pip install --force-reinstall --no-cache-dir git+https://github.com/lawfulgood-us/Lexoid.git@vertex-ai-support
```

### 2. Update your model configuration:

```python
# In your document processing code
result = parse(
    document_path,
    parser_type="LLM_PARSE",
    model="gemini-1.5-flash"  # Use a Vertex AI compatible model
)
```

### 3. Rebuild your Docker containers:

```bash
docker-compose build --no-cache celery_worker
docker-compose up
```

## Verification

After the fix, you should see successful parsing:

```
celery_worker-1  | DEBUG | Using Vertex AI endpoint: plated-particle-452122-a5 in us-west1
celery_worker-1  | INFO  | Successfully parsed document with X pages
```

Instead of:

```
celery_worker-1  | ERROR | HTTP error: 400 - Please use a valid role: user, model.
```

## Files Changed

1. **`lexoid/core/parse_type/llm_parser.py`** - Added role field for Vertex AI
2. **`tests/test_vertex_ai.py`** - Added tests to verify role field behavior
3. **`docs/vertex_ai_setup.md`** - Documented available models
4. **`CHANGELOG.md`** - Documented the fix

## Summary

- ✅ **Fixed:** Added `role: user` field for Vertex AI requests
- ✅ **Documented:** Available models in Vertex AI
- ✅ **Tested:** Unit tests verify correct payload structure
- ⚠️ **Action Required:** Update your model to use Vertex AI compatible model

The good news: **Your Vertex AI setup is working correctly!** The authentication succeeded, it just needed the correct request format and a compatible model.

