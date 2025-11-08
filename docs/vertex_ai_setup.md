# Using Vertex AI with Lexoid

This guide explains how to configure Lexoid to use Google Cloud Vertex AI instead of the public Gemini API endpoint for enhanced data privacy and security.

## Why Vertex AI?

Vertex AI provides:
- **Enhanced data privacy** - Your data stays within your Google Cloud project
- **Compliance** - Meets enterprise-grade security and compliance requirements
- **Data residency** - Control where your data is processed
- **VPC integration** - Can be used within your private network
- **Audit logging** - Complete audit trails for compliance

This makes it ideal for sensitive applications like legal document processing.

## Setup Instructions

### 1. Install Dependencies

First, install the required dependencies:

```bash
poetry install
# or
pip install google-cloud-aiplatform
```

### 2. Set Up Google Cloud Project

1. Create a Google Cloud project (or use an existing one)
2. Enable the Vertex AI API:
   ```bash
   gcloud services enable aiplatform.googleapis.com
   ```

3. Set up authentication:

#### For Local Development

```bash
# Authenticate with your Google account
gcloud auth application-default login
```

#### For Cloud Run (Production)

```bash
# Create a service account for your Cloud Run service
gcloud iam service-accounts create lexoid-vertex-ai \
    --display-name="Lexoid Vertex AI Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:lexoid-vertex-ai@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# The service account will be automatically attached when deploying Cloud Run
# No need to download or manage keys!
```

### 3. Configure Environment Variables

Set the following environment variables to enable Vertex AI mode:

```bash
# Required: Your Google Cloud project ID (use either variable name)
export GCP_PROJECT="your-project-id"
# OR
export GOOGLE_CLOUD_PROJECT="your-project-id"  # Standard GCP variable

# Optional: Region (defaults to us-west1)
export GCP_REGION="us-west1"
# OR
export GOOGLE_CLOUD_REGION="us-west1"  # Standard GCP variable
```

You can also create a `.env` file:

```env
# Lexoid will check both GCP_PROJECT and GOOGLE_CLOUD_PROJECT
GCP_PROJECT=your-project-id
GCP_REGION=us-west1

# Setting both prevents warnings from Google Cloud SDK:
GOOGLE_CLOUD_PROJECT=your-project-id
```

**Authentication** is handled automatically via Application Default Credentials (ADC):
- **Locally**: Uses credentials from `gcloud auth application-default login`
- **In Cloud Run**: Uses the attached service account automatically

**Note:** Setting `GOOGLE_CLOUD_PROJECT` in addition to `GCP_PROJECT` will suppress warnings from the Google Cloud SDK libraries.

## Usage

### Basic Usage

Once configured, Lexoid will automatically use Vertex AI when the `GCP_PROJECT` environment variable is set:

```python
from lexoid import parse

# This will automatically use Vertex AI if configured
result = parse(
    "document.pdf",
    parser_type="LLM_PARSE",
    model="gemini-2.0-flash"  # or gemini-1.5-pro, gemini-1.5-flash
)

print(result["raw"])
```

### Switching Between Gemini API and Vertex AI

**Using Standard Gemini API:**
```python
import os

# Use public Gemini API (no Vertex AI variables)
os.environ["GOOGLE_API_KEY"] = "your-api-key"
# Ensure GCP_PROJECT is not set
if "GCP_PROJECT" in os.environ:
    del os.environ["GCP_PROJECT"]

result = parse("document.pdf", parser_type="LLM_PARSE")
```

**Using Vertex AI:**
```python
import os

# Use Vertex AI
os.environ["GCP_PROJECT"] = "your-project-id"
os.environ["GCP_REGION"] = "us-west1"
# GOOGLE_API_KEY is not needed for Vertex AI

result = parse("document.pdf", parser_type="LLM_PARSE")
```

### Available Models

**⚠️ IMPORTANT:** Gemini 1.5 models were deprecated on September 24, 2025 and are no longer available.

Vertex AI currently supports these Gemini models for document parsing:

**Recommended for Production:**
- ⭐ **`gemini-2.0-flash-exp`** - Fast, cost-effective, good accuracy (RECOMMENDED)
- **`gemini-2.5-flash`** - Generally Available (GA), better accuracy
- **`gemini-2.5-pro`** - Highest accuracy for complex documents (slower, more expensive)

**Legacy (Deprecated):**
- ❌ ~~`gemini-1.5-flash`~~ - DEPRECATED (September 24, 2025)
- ❌ ~~`gemini-1.5-pro`~~ - DEPRECATED (September 24, 2025)
- ❌ ~~`gemini-1.0-pro`~~ - DEPRECATED

**For Legal Document Parsing:**
- Use **`gemini-2.0-flash-exp`** for most documents (fast, cost-effective)
- Use **`gemini-2.5-pro`** for complex contracts with tables and charts (highest accuracy)

**Note:** Check the [Vertex AI model documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models) for the latest availability in your region.

### Example: Legal Document Processing

```python
import os
from dotenv import load_dotenv
from lexoid import parse

# Load environment variables
load_dotenv()

# Verify Vertex AI is configured
if not os.environ.get("GCP_PROJECT"):
    raise ValueError("GCP_PROJECT must be set for privacy-compliant processing")

# Parse legal document with Vertex AI
result = parse(
    "sensitive_legal_document.pdf",
    parser_type="LLM_PARSE",
    model="gemini-2.0-flash-exp",  # Use current model
    temperature=0.0,  # Deterministic output
)

# Extract the content
markdown_content = result["raw"]
segments = result["segments"]

# Process each page
for segment in segments:
    page_num = segment["metadata"]["page"]
    content = segment["content"]
    print(f"Page {page_num}:\n{content}\n")

# Token usage for cost tracking
print(f"Total tokens used: {result['token_usage']['total']}")
```

## Verification

To verify that Vertex AI is being used, check the logs:

```python
from loguru import logger
import sys

# Enable debug logging
logger.remove()
logger.add(sys.stderr, level="DEBUG")

result = parse("document.pdf", parser_type="LLM_PARSE")
```

You should see log output like:
```
Using Vertex AI endpoint: your-project-id in us-west1
```

## Troubleshooting

### Authentication Errors

If you see authentication errors:

**Locally:**
1. Run `gcloud auth application-default login` to authenticate
2. Ensure you have the `roles/aiplatform.user` role on the project
3. Verify with: `gcloud auth application-default print-access-token`

**In Cloud Run:**
1. Verify the service account is attached to your Cloud Run service
2. Check the service account has the `roles/aiplatform.user` role
3. Ensure the Vertex AI API is enabled in your project

### Permission Denied

```bash
# Grant necessary permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:YOUR_SERVICE_ACCOUNT@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"
```

### Region/Location Issues

If you get location errors, verify the region is supported:
```python
# Common regions: us-west1, us-east1, europe-west1, asia-southeast1
export GCP_REGION="us-west1"
```

### Testing Connection

Quick test to verify Vertex AI connectivity:

```python
from lexoid.core.parse_type.llm_parser import parse_image_with_gemini
import base64
import os

# Verify environment
print(f"Project ID: {os.environ.get('GCP_PROJECT')}")
print(f"Location: {os.environ.get('GCP_REGION', 'us-west1')}")

# Test with a simple image
with open("test_image.png", "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

result = parse_image_with_gemini(
    base64_file=image_data,
    mime_type="image/png",
    model="gemini-2.0-flash",
    pages_per_split_=1
)

print("Success! Vertex AI is working.")
print(f"Response: {result['raw'][:100]}...")
```

## Cost Considerations

Vertex AI pricing may differ from the public Gemini API. Check the [Vertex AI pricing page](https://cloud.google.com/vertex-ai/pricing) for current rates.

Enable cost tracking in your code:

```python
result = parse(
    "document.pdf",
    parser_type="LLM_PARSE",
    api_cost_mapping="path/to/api_cost_mapping.json"
)

print(f"Estimated cost: ${result['token_cost']['total']:.4f}")
```

## Security Best Practices

1. **Use Application Default Credentials** - No need to manage or rotate keys
2. **Use dedicated service accounts** - Create separate service accounts for Cloud Run services
3. **Restrict permissions** - Grant only `roles/aiplatform.user`, not broader roles
4. **Enable audit logs** - Use Cloud Audit Logs for compliance tracking
5. **Network security** - Consider using VPC Service Controls for additional isolation
6. **Principle of least privilege** - Only grant permissions needed for your use case

## Additional Resources

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Service Account Best Practices](https://cloud.google.com/iam/docs/best-practices-service-accounts)
- [Vertex AI Security](https://cloud.google.com/vertex-ai/docs/general/security)

