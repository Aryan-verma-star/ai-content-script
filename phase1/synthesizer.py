"""Synthesizer module for AI Content Engine Phase 1.

Takes raw scraped data, constructs LLM prompts, calls the LLM API,
parses the response, and writes a structured Trend_Brief.json file.
"""

import json
import logging
from datetime import datetime
from typing import Any

import anthropic
import openai

from phase1.config import config

logger = logging.getLogger(__name__)


MAX_CONTEXT_LENGTH = 500


def clean_data(raw: dict[str, Any]) -> str:
    """Clean and format raw scraped data into a compact text block.

    Iterates over all platforms in raw data and builds a compact
    text representation for each item.

    Args:
        raw: The raw scraped data dictionary containing youtube,
            tiktok, and instagram lists.

    Returns:
        A single string with all content blocks joined by "---".
    """
    blocks = []

    for platform in ["youtube", "tiktok", "instagram"]:
        items = raw.get(platform, [])
        for item in items:
            if platform == "youtube":
                title = item.get("title", "")
                views = item.get("view_count", 0)
                likes = item.get("like_count", 0)
                transcript = item.get("transcript", "")
            elif platform == "tiktok":
                title = item.get("title", "")
                views = item.get("view_count", 0)
                likes = item.get("like_count", 0)
                transcript = item.get("transcript", "")
            else:
                title = item.get("caption", "")[:100]
                views = item.get("view_count", 0)
                likes = item.get("like_count", 0)
                transcript = item.get("transcript", "")

            transcript_preview = (
                transcript[:MAX_CONTEXT_LENGTH]
                if len(transcript) > MAX_CONTEXT_LENGTH
                else transcript
            )

            block = (
                f"[{platform.upper()}] {title} | Views: {views} | Likes: {likes}\n"
                f"Transcript/Hook: {transcript_preview}"
            )
            blocks.append(block)

    return "\n---\n".join(blocks)


def build_prompt(niche: str, context_block: str) -> str:
    """Construct the LLM prompt for trend analysis.

    Creates a structured prompt that instructs the LLM to analyze
    trending content and respond with a specific JSON schema.

    Args:
        niche: The target niche for trend analysis.
        context_block: The cleaned content data block.

    Returns:
        The complete prompt string for the LLM.
    """
    prompt = f'''You are a viral content strategist. Analyze the following trending content data for the niche: "{niche}".

CONTENT DATA:
{context_block}

Based on this data, respond ONLY with a valid JSON object in the following exact schema. Do not include markdown fences, explanations, or any text outside the JSON:

{{
  "niche": "<the niche>",
  "generated_at": "<ISO 8601 timestamp>",
  "top_themes": [
    {{"theme": "<theme 1>", "rationale": "<one sentence why this is trending>"}},
    {{"theme": "<theme 2>", "rationale": "<one sentence why this is trending>"}},
    {{"theme": "<theme 3>", "rationale": "<one sentence why this is trending>"}}
  ],
  "hook_examples": [
    "<hook 1 — an attention-grabbing opening line inspired by the data>",
    "<hook 2>",
    "<hook 3>"
  ],
  "emerging_trend": {{
    "trend": "<one emerging trend not yet mainstream>",
    "evidence": "<which video/post supports this and why>"
  }}
}}'''
    return prompt


def call_llm(prompt: str) -> str:
    """Call the configured LLM API with the given prompt.

    Uses either OpenAI or Anthropic based on configuration.

    Args:
        prompt: The prompt to send to the LLM.

    Returns:
        The raw response content from the LLM.

    Raises:
        ValueError: If LLM_PROVIDER is not set to 'openai' or 'anthropic'.
    """
    provider = config.llm_provider

    if provider == "openai":
        client = openai.OpenAI(api_key=config.openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif provider == "anthropic":
        client = anthropic.Anthropic(api_key=config.anthropic_api_key)
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    else:
        raise ValueError(
            f"Invalid LLM_PROVIDER: '{provider}'. Must be 'openai' or 'anthropic'."
        )


def parse_and_validate(llm_response: str) -> dict[str, Any]:
    """Parse and validate the LLM JSON response.

    Attempts to parse the LLM response as JSON and validates that
    all required keys and structures are present.

    Args:
        llm_response: The raw JSON string from the LLM.

    Returns:
        The parsed and validated dictionary.

    Raises:
        ValueError: If parsing or validation fails.
    """
    try:
        parsed = json.loads(llm_response.strip())
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse LLM JSON response: {e}")

    required_keys = ["niche", "generated_at", "top_themes", "hook_examples", "emerging_trend"]
    for key in required_keys:
        if key not in parsed:
            raise ValueError(f"Missing required key in LLM response: {key}")

    if not isinstance(parsed["top_themes"], list) or len(parsed["top_themes"]) != 3:
        raise ValueError(
            f"top_themes must be a list with exactly 3 items, "
            f"got {len(parsed.get('top_themes', []))}"
        )

    if not isinstance(parsed["hook_examples"], list) or len(parsed["hook_examples"]) != 3:
        raise ValueError(
            f"hook_examples must be a list with exactly 3 items, "
            f"got {len(parsed.get('hook_examples', []))}"
        )

    return parsed


def run_synthesizer(raw_data: dict[str, Any]) -> dict[str, Any]:
    """Execute the full synthesis pipeline.

    Takes raw scraped data, cleans it, builds a prompt, calls the LLM,
    parses and validates the response, and writes Trend_Brief.json.

    Args:
        raw_data: The raw scraped data from run_scraper().

    Returns:
        The validated and parsed Trend_Brief dictionary.

    Raises:
        Exception: If any step in the pipeline fails.
    """
    logger.info("Starting synthesis pipeline")

    context_block = clean_data(raw_data)
    niche = raw_data.get("niche", "")

    prompt = build_prompt(niche, context_block)

    try:
        llm_response = call_llm(prompt)
    except Exception as e:
        logger.error(f"LLM API call failed: {e}")
        raise

    try:
        parsed = parse_and_validate(llm_response)
    except Exception as e:
        logger.debug(f"Raw LLM response: {llm_response}")
        logger.error(f"Parse/validate failed: {e}")
        raise

    import os

    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "Trend_Brief.json")
    with open(output_path, "w") as f:
        json.dump(parsed, f, indent=2)

    logger.info(f"Trend_Brief.json written to {output_path}")
    print(f"[Phase 1] Synthesis complete. Trend_Brief.json written to {output_path}")

    return parsed