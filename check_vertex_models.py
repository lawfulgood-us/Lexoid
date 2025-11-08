#!/usr/bin/env python3
"""
Script to check which Gemini models are available in your Vertex AI region
"""
import os
from lexoid import parse

def test_model(model_name, test_file="test_sample.pdf"):
    """Test if a model is available and working"""
    print(f"\n🧪 Testing {model_name}...")
    
    try:
        # Try to parse a small document
        result = parse(
            test_file,
            parser_type="LLM_PARSE",
            model=model_name,
            pages_per_split=1,  # Just test with 1 page
            max_processes=1
        )
        
        if result and result.get("raw"):
            print(f"   ✅ {model_name} - AVAILABLE and working")
            print(f"      Tokens used: {result['token_usage']['total']}")
            return True
        else:
            print(f"   ❌ {model_name} - Failed (no response)")
            return False
            
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "not found" in error_msg.lower():
            print(f"   ❌ {model_name} - NOT AVAILABLE in this region")
        elif "400" in error_msg:
            print(f"   ⚠️  {model_name} - Available but request format issue")
        else:
            print(f"   ❌ {model_name} - Error: {error_msg[:100]}")
        return False


def main():
    """Check availability of Gemini models"""
    
    # Check environment
    project = os.environ.get("GCP_PROJECT")
    region = os.environ.get("GCP_REGION", "us-west1")
    
    if not project:
        print("❌ Error: GCP_PROJECT environment variable not set")
        print("   Set it with: export GCP_PROJECT=your-project-id")
        return
    
    print("=" * 60)
    print("🔍 Vertex AI Model Availability Check")
    print("=" * 60)
    print(f"📍 Project: {project}")
    print(f"🌍 Region: {region}")
    print("=" * 60)
    
    # Models to test
    models = [
        # Production GA models
        ("gemini-1.5-flash", "GA - Recommended"),
        ("gemini-1.5-pro", "GA - High accuracy"),
        ("gemini-1.0-pro", "GA - Legacy"),
        
        # Experimental/Preview models
        ("gemini-2.0-flash-exp", "Experimental"),
        ("gemini-2.5-flash", "Preview"),
        ("gemini-2.5-pro", "Preview"),
        ("gemini-2.5-flash-lite", "Preview - Limited availability"),
    ]
    
    print("\n📋 Testing models (this may take a few minutes)...\n")
    
    available = []
    unavailable = []
    
    for model_name, status in models:
        result = test_model(model_name)
        if result:
            available.append((model_name, status))
        else:
            unavailable.append((model_name, status))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    print(f"\n✅ Available Models ({len(available)}):")
    for model, status in available:
        print(f"   • {model} ({status})")
    
    print(f"\n❌ Unavailable Models ({len(unavailable)}):")
    for model, status in unavailable:
        print(f"   • {model} ({status})")
    
    # Recommendation
    print("\n" + "=" * 60)
    print("💡 RECOMMENDATION")
    print("=" * 60)
    
    if ("gemini-2.5-flash", "Preview") in available:
        print("\n🎉 Gemini 2.5 Flash is available in your region!")
        print("\nYou have two good options:")
        print("\n1. Conservative (Production):")
        print("   model = 'gemini-1.5-flash'  # GA, stable, proven")
        print("\n2. Cutting-edge (Preview):")
        print("   model = 'gemini-2.5-flash'  # Better accuracy, preview status")
        print("\n⚠️  Note: Preview models may have breaking changes")
    else:
        print("\n✅ Use Gemini 1.5 Flash (GA - Production Ready)")
        print("   model = 'gemini-1.5-flash'")
        print("\n❌ Gemini 2.5 models not available in your region yet")


if __name__ == "__main__":
    main()

