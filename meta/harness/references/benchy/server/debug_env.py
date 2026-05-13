#!/usr/bin/env python3

import os
from dotenv import load_dotenv

print("=== Environment Debug Script ===")
print(f"Current working directory: {os.getcwd()}")

# Check environment before loading dotenv
print(f"\n1. OPENAI_API_KEY from environment (before dotenv): {os.getenv('OPENAI_API_KEY', 'NOT FOUND')}")

# Load dotenv from current directory
print(f"\n2. Loading .env from current directory...")
load_dotenv()
key_after_load = os.getenv('OPENAI_API_KEY', 'NOT FOUND')
print(f"OPENAI_API_KEY after load_dotenv(): {key_after_load}")

if key_after_load != 'NOT FOUND':
    print(f"Key length: {len(key_after_load)}")
    print(f"Key starts with: {key_after_load[:10]}...")
    print(f"Key ends with: ...{key_after_load[-10:]}")

# Try loading from parent directory
print(f"\n3. Loading .env from parent directory...")
parent_env_path = os.path.join(os.path.dirname(os.getcwd()), '.env')
print(f"Parent .env path: {parent_env_path}")
load_dotenv(parent_env_path)
key_after_parent_load = os.getenv('OPENAI_API_KEY', 'NOT FOUND')
print(f"OPENAI_API_KEY after loading parent .env: {key_after_parent_load}")

if key_after_parent_load != 'NOT FOUND':
    print(f"Key length: {len(key_after_parent_load)}")
    print(f"Key starts with: {key_after_parent_load[:10]}...")
    print(f"Key ends with: ...{key_after_parent_load[-10:]}")

# Check for any potential environment variable conflicts
print(f"\n4. Checking all environment variables containing 'OPENAI':")
for key, value in os.environ.items():
    if 'OPENAI' in key.upper():
        print(f"  {key}: {value[:10]}...{value[-10:] if len(value) > 20 else value}")

print(f"\n5. Checking if .env files exist:")
current_env = os.path.join(os.getcwd(), '.env')
parent_env = os.path.join(os.path.dirname(os.getcwd()), '.env')
print(f"Current directory .env exists: {os.path.exists(current_env)}")
print(f"Parent directory .env exists: {os.path.exists(parent_env)}")

if os.path.exists(current_env):
    with open(current_env, 'r') as f:
        content = f.read()
        if 'OPENAI_API_KEY' in content:
            for line in content.split('\n'):
                if line.startswith('OPENAI_API_KEY'):
                    print(f"Current .env OPENAI_API_KEY line: {line}")

if os.path.exists(parent_env):
    with open(parent_env, 'r') as f:
        content = f.read()
        if 'OPENAI_API_KEY' in content:
            for line in content.split('\n'):
                if line.startswith('OPENAI_API_KEY'):
                    print(f"Parent .env OPENAI_API_KEY line: {line}")