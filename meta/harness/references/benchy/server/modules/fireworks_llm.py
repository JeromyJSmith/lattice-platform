import os
import requests
import json

from modules.data_types import (
    BenchPromptResponse,
    PromptResponse,
    ThoughtResponse,
)
from utils import deepseek_r1_distil_separate_thoughts_and_response
import time


from dotenv import load_dotenv

load_dotenv()

FIREWORKS_API_KEY = os.getenv("FIREWORKS_AI_API_KEY", "")

API_URL = "https://api.fireworks.ai/inference/v1/completions"


def get_fireworks_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    # For now, just return 0.0 or substitute a real cost calculation if available
    return 0.0


def bench_prompt(prompt: str, model: str) -> BenchPromptResponse:

    start_time = time.time()
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {FIREWORKS_API_KEY}",
    }
    payload = {
        "model": model,
        "max_tokens": 20480,
        "prompt": prompt,
        "temperature": 0.2,
    }

    response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
    end_time = time.time()

    resp_json = response.json()
    content = ""
    if "choices" in resp_json and len(resp_json["choices"]) > 0:
        content = resp_json["choices"][0].get("text", "")

    return BenchPromptResponse(
        response=content,
        tokens_per_second=0.0,  # or compute if available
        provider="fireworks",
        total_duration_ms=(end_time - start_time) * 1000,
        load_duration_ms=0.0,
        errored=not response.ok,
    )


def text_prompt(prompt: str, model: str) -> PromptResponse:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {FIREWORKS_API_KEY}",
    }
    payload = {
        "model": model,
        "max_tokens": 20480,
        "prompt": prompt,
        "temperature": 0.0,
    }

    response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
    resp_json = response.json()

    print("resp_json", resp_json)

    # Extract just the text from the first choice
    content = ""
    if "choices" in resp_json and len(resp_json["choices"]) > 0:
        content = resp_json["choices"][0].get("text", "")

    return PromptResponse(
        response=content,
        runTimeMs=0,  # or compute if desired
        inputAndOutputCost=0.0,  # or compute if you have cost details
    )


def thought_prompt(prompt: str, model: str) -> ThoughtResponse:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {FIREWORKS_API_KEY}",
    }
    payload = {
        "model": model,
        "max_tokens": 20480,
        "prompt": prompt,
        "temperature": 0.2,
    }

    response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
    resp_json = response.json()

    content = ""
    if "choices" in resp_json and len(resp_json["choices"]) > 0:
        content = resp_json["choices"][0].get("text", "")

    if "r1" in model:
        thoughts, response_content = deepseek_r1_distil_separate_thoughts_and_response(
            content
        )
    else:
        thoughts = ""
        response_content = content

    return ThoughtResponse(
        thoughts=thoughts,
        response=response_content,
        error=None if response.ok else str(resp_json.get("error", "Unknown error")),
    )
