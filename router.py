#!/usr/bin/env python3
"""
Router Management Script for LiteLLM
=====================================
Create, update, and manage auto-routers via the LiteLLM API.

Usage:
  python router.py create <name> --routes <routes.json>
  python router.py create <name> --preset <coding|reasoning|quick|creative>
  python router.py list
  python router.py delete <model_id>

Examples:
  # Create a custom router from JSON file
  python router.py create MyRouter --routes my_routes.json

  # Create using a preset configuration
  python router.py create CodeHelper --preset coding

  # List all models
  python router.py list

Environment:
  LITELLM_URL - API URL (default: https://ai.nirmaker.com)
  LITELLM_API_KEY - API key for authentication
"""

import argparse
import json
import os
import http.client
import ssl
from urllib.parse import urlparse

# =============================================================================
# Configuration
# =============================================================================

API_URL = os.environ.get("LITELLM_URL", "https://ai.nirmaker.com")
API_KEY = os.environ.get("LITELLM_API_KEY", "dummy-key")
EMBEDDING_MODEL = "mistral/mistral-embed"

# =============================================================================
# Preset Configurations
# =============================================================================

PRESETS = {
    "coding": {
        "default_model": "mistral/codestral-2508",
        "routes": [
            {
                "name": "mistral/codestral-2508",
                "description": "Primary: Code generation (256K ctx), FIM, 80+ languages",
                "utterances": [
                    "write function", "implement algorithm", "code this", "create class",
                    "build API", "develop feature", "program this", "write code",
                    "implement in", "code solution", "create code"
                ],
                "score_threshold": 0.30
            },
            {
                "name": "mistral/devstral-medium-2507",
                "description": "Agentic coding (61.6% SWE-Bench), multi-file",
                "utterances": [
                    "fix bug", "debug", "find error", "troubleshoot", "why doesn't work",
                    "fix code", "solve issue", "diagnose", "trace error"
                ],
                "score_threshold": 0.35
            },
            {
                "name": "groq/openai/gpt-oss-120b",
                "description": "120B GPT, code reasoning, ~500 tok/s",
                "utterances": [
                    "explain code", "how does this work", "code review", "analyze code",
                    "what does this do", "understand code", "review implementation"
                ],
                "score_threshold": 0.40
            }
        ]
    },
    "reasoning": {
        "default_model": "groq/llama-3.3-70b-versatile",
        "routes": [
            {
                "name": "groq/llama-3.3-70b-versatile",
                "description": "70B Llama-3.3, ~280 tok/s, 131K ctx",
                "utterances": [
                    "analyze", "think about", "reason", "evaluate", "consider",
                    "analysis", "logical", "think carefully"
                ],
                "score_threshold": 0.30
            },
            {
                "name": "groq/deepseek-r1-distill-llama-70b",
                "description": "DeepSeek R1, 94.5% MATH-500",
                "utterances": [
                    "solve mathematically", "calculate", "prove", "math problem",
                    "equation", "theorem", "compute", "work out"
                ],
                "score_threshold": 0.35
            },
            {
                "name": "gemini/gemini-2.5-flash",
                "description": "Gemini 2.5, 1M ctx, multimodal",
                "utterances": [
                    "complex problem", "multi-step", "detailed reasoning",
                    "comprehensive analysis", "in-depth", "deep dive"
                ],
                "score_threshold": 0.40
            }
        ]
    },
    "quick": {
        "default_model": "groq/llama-3.1-8b-instant",
        "routes": [
            {
                "name": "groq/llama-3.1-8b-instant",
                "description": "8B Llama, ultra-fast, simple queries",
                "utterances": [
                    "what is", "define", "who is", "when was", "where is",
                    "quick", "simple", "briefly", "short answer"
                ],
                "score_threshold": 0.25
            },
            {
                "name": "gemini/gemini-2.5-flash-lite",
                "description": "Flash Lite, ~392 tok/s, low cost",
                "utterances": [
                    "translate", "convert", "transform", "change to", "in another language"
                ],
                "score_threshold": 0.30
            },
            {
                "name": "mistral/open-mistral-7b",
                "description": "Open Mistral 7B, lightweight",
                "utterances": [
                    "summarize", "tldr", "key points", "main idea", "gist", "sum up"
                ],
                "score_threshold": 0.30
            }
        ]
    },
    "creative": {
        "default_model": "groq/moonshotai/kimi-k2-instruct",
        "routes": [
            {
                "name": "groq/moonshotai/kimi-k2-instruct",
                "description": "Kimi K2, 32B MoE, storytelling",
                "utterances": [
                    "write story", "tell story", "narrative", "fiction", "novel",
                    "short story", "tale", "once upon a time"
                ],
                "score_threshold": 0.30
            },
            {
                "name": "groq/moonshotai/kimi-k2-instruct-0905",
                "description": "Kimi K2 updated, enhanced creative",
                "utterances": [
                    "poem", "poetry", "verse", "rhyme", "compose poem", "haiku", "sonnet"
                ],
                "score_threshold": 0.35
            },
            {
                "name": "mistral/open-mistral-nemo",
                "description": "Mistral Nemo 12B, multilingual",
                "utterances": [
                    "email", "letter", "message", "draft", "formal letter",
                    "business email", "professional message"
                ],
                "score_threshold": 0.35
            }
        ]
    }
}

# =============================================================================
# API Functions
# =============================================================================

def create_connection():
    """Create HTTPS connection to API"""
    parsed = urlparse(API_URL)
    context = ssl.create_default_context()
    if parsed.scheme == "https":
        return http.client.HTTPSConnection(parsed.netloc, context=context)
    return http.client.HTTPConnection(parsed.netloc)


def api_request(method: str, path: str, body: dict = None) -> tuple:
    """Make API request and return (status, response_dict)"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    conn = create_connection()
    try:
        conn.request(method, path, body=json.dumps(body) if body else None, headers=headers)
        response = conn.getresponse()
        data = response.read().decode("utf-8")
        try:
            return response.status, json.loads(data)
        except:
            return response.status, {"raw": data}
    finally:
        conn.close()


def create_router(name: str, routes: list, default_model: str):
    """Create an auto-router"""
    print(f"\n{'='*60}")
    print(f"Creating router: {name}")
    print(f"Default model: {default_model}")
    print(f"Number of routes: {len(routes)}")
    print(f"{'='*60}")
    
    payload = {
        "model_name": name,
        "litellm_params": {
            "model": f"auto_router/{name}",
            "auto_router_config": json.dumps({"routes": routes}),
            "auto_router_default_model": default_model,
            "auto_router_embedding_model": EMBEDDING_MODEL
        },
        "model_info": {"health_check": False}
    }
    
    status, response = api_request("POST", "/model/new", payload)
    
    if status == 200:
        print(f"✅ Router '{name}' created successfully!")
        print(f"   Model ID: {response.get('model_id', 'N/A')}")
        return True
    else:
        print(f"❌ Failed to create router")
        print(f"   Status: {status}")
        print(f"   Error: {json.dumps(response, indent=2)[:500]}")
        return False


def list_models():
    """List all models"""
    print(f"\nFetching models from {API_URL}...")
    
    status, response = api_request("GET", "/model/info")
    
    if status == 200:
        models = response.get("data", [])
        print(f"\n{'='*60}")
        print(f"Found {len(models)} models")
        print(f"{'='*60}")
        for model in models:
            model_name = model.get("model_name", "Unknown")
            model_id = model.get("model_info", {}).get("id", "N/A")
            litellm_model = model.get("litellm_params", {}).get("model", "N/A")
            print(f"\n  • {model_name}")
            print(f"    ID: {model_id}")
            print(f"    Model: {litellm_model}")
    else:
        print(f"❌ Failed to list models: {status}")
        print(response)


def delete_model(model_id: str):
    """Delete a model by ID"""
    print(f"\nDeleting model: {model_id}")
    
    status, response = api_request("POST", "/model/delete", {"id": model_id})
    
    if status == 200:
        print(f"✅ Model deleted successfully!")
    else:
        print(f"❌ Failed to delete model: {status}")
        print(response)


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Router Management for LiteLLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create router from preset
  python router.py create MyCoder --preset coding
  
  # Create router from JSON file
  python router.py create MyRouter --routes routes.json --default groq/llama-3.3-70b-versatile
  
  # List all models
  python router.py list
  
  # Delete a model
  python router.py delete <model-id>

JSON Routes Format:
  [
    {
      "name": "model/name",
      "description": "Description",
      "utterances": ["keyword1", "keyword2"],
      "score_threshold": 0.35
    }
  ]
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # create command
    create_parser = subparsers.add_parser("create", help="Create a new router")
    create_parser.add_argument("name", help="Router name")
    create_parser.add_argument("--preset", choices=PRESETS.keys(), help="Use preset configuration")
    create_parser.add_argument("--routes", help="Path to routes JSON file")
    create_parser.add_argument("--default", help="Default model (required with --routes)")
    
    # list command
    subparsers.add_parser("list", help="List all models")
    
    # delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a model")
    delete_parser.add_argument("model_id", help="Model ID to delete")
    
    args = parser.parse_args()
    
    if args.command == "create":
        if args.preset:
            preset = PRESETS[args.preset]
            create_router(args.name, preset["routes"], preset["default_model"])
        elif args.routes:
            if not args.default:
                print("❌ --default is required when using --routes")
                return
            with open(args.routes) as f:
                routes = json.load(f)
            create_router(args.name, routes, args.default)
        else:
            print("❌ Either --preset or --routes is required")
    
    elif args.command == "list":
        list_models()
    
    elif args.command == "delete":
        delete_model(args.model_id)


if __name__ == "__main__":
    main()
