"""Synthesizer module for AI Content Engine Phase 1.

Takes raw scraped data, constructs LLM prompts, calls the LLM API,
parses the response, and writes a structured Trend_Brief.json file.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any

import anthropic
import httpx
import requests
import openai

from phase1.config import config

logger = logging.getLogger(__name__)


def _create_openai_client(
    api_key: str, base_url: str | None = None
) -> "openai.OpenAI":
    """Create an OpenAI client that ignores environment proxy settings.

    Args:
        api_key: The API key for authentication.
        base_url: Optional base URL for OpenAI-compatible APIs.

    Returns:
        Configured OpenAI client.
    """
    http_client = httpx.Client(trust_env=False)
    return openai.OpenAI(
        api_key=api_key,
        base_url=base_url,
        http_client=http_client,
    )


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
    """Construct the LLM prompt for deep viral content analysis.

    Args:
        niche: The target niche for trend analysis.
        context_block: The cleaned content data block.

    Returns:
        The complete prompt string for the LLM.
    """
    from datetime import datetime
    
    prompt = f'''You will receive a raw context_block containing scraped YouTube transcripts, TikTok metadata, and trending video titles from a specific niche. Your sole function is to deconstruct this data and output a structured JSON analysis that reveals the deep psychological and structural mechanics driving virality in this niche.

ABSOLUTE CONSTRAINTS — VIOLATIONS WILL INVALIDATE YOUR OUTPUT:

BANNED PHRASES & CLICHÉS:
You are STRICTLY FORBIDDEN from generating, referencing, or paraphrasing any of the following phrases or their semantic equivalents in any field of your output:
"Stop scrolling"
"Watch to the end"
"The secret to..."
"This one trick..."
"You won't believe..."
"Game changer"
"Life-changing"
"Actionable advice"
"Level up"
"Crush it"
"Hustle"
Any hook that begins with a direct second-person command as its sole opener (e.g., "Do this every morning")
If a cliché is detected in your output during self-review, rewrite that field before finalizing. Specificity and novelty are non-negotiable.

EVIDENCE REQUIREMENT:
Every claim about a trend, angle, or framework MUST be anchored to a direct quote or paraphrase from the context_block. Do not invent trends. Do not project patterns that are not present in the data.

PSYCHOLOGICAL PRECISION:
Generic psychological labels (e.g., "motivation," "inspiration") are not acceptable. You must identify the precise psychological mechanism at work. Use established behavioral and cognitive frameworks where applicable:

FOMO (Fear of Missing Out)
Status Anxiety
Identity Reinforcement
Cognitive Dissonance Exploitation
Negative Constraint Framing
Sunk Cost Validation
Aspirational Identity Gap
In-Group/Out-Group Signaling
Loss Aversion
Competence Threat
If the trigger does not map cleanly to one of the above, name and define it precisely.
HOOK ANATOMY — NOT COPYWRITING:
You are NOT being asked to write catchy hooks from scratch. You are being asked to REVERSE-ENGINEER the structural formula of hooks that are already proven to work in the raw data. Output the skeleton, not the flesh. The format must be a reusable framework (e.g., "[Counterintuitive Outcome] + [Implied Villain] + [Credibility Signal]"), not a finished line of copy.

RETENTION MECHANICS — STRUCTURAL ONLY:
Identify structural and pacing techniques used within the body of the transcripts — not surface-level observations. Examples of acceptable mechanics:

"Open loop seeded at 0:12, resolved at 2:47 — creates sustained curiosity tension"
"Rapid context switching every 18–22 seconds to reset attention decay"
"Micro-promise stacking: three sequential 'and then I'll show you...' anchors before the payoff"
"Bait-and-switch: problem framed as external, resolution reframed as internal"
Do NOT output: "The video uses storytelling" or "The creator is engaging." These are observations, not mechanics.
ANALYSIS PROTOCOL:

Step 1 — Niche Calibration:
Identify the niche from the context_block. Then identify the single deepest psychological desire driving viewership in this niche RIGHT NOW — not what the audience says they want, but what the engagement data implies they actually need. Distinguish between surface desire (e.g., "make more money") and core desire (e.g., "proof that my current path is not a permanent failure").

Step 2 — Framework Extraction:
Identify 2–4 distinct content angles that are generating the highest engagement signals in the data. For each, name the angle archetype, map it to its psychological trigger, and cite transcript evidence.

Step 3 — Hook Deconstruction:
Extract 2–4 hook frameworks from the highest-performing titles and opening transcript lines. Output the structural formula only. Then, using that formula, generate ONE highly specific, non-clichéd example tailored to the niche data — not a generic fill-in.

Step 4 — Retention Mechanics Audit:
Scan the transcript bodies for 2–4 structural retention techniques. Be specific about timing, sequencing, and mechanism. Name the technique if it has an established name (e.g., "open loop," "pattern interrupt," "false resolution").

Step 5 — Self-Review:
Before finalizing output, scan every string value in your JSON for banned phrases, vague psychological labels, and unsupported claims. Rewrite any field that fails this check.

INPUT:

{context_block}

OUTPUT INSTRUCTIONS:

Output ONLY valid, minified JSON. No markdown. No code fences. No preamble. No explanation. No trailing commentary.
Your entire response must begin with {{ and end with }}.
Strictly conform to the following schema. Do not add, remove, or rename any keys.
REQUIRED OUTPUT SCHEMA:

{{
"niche_analysis": {{
"niche": "<Identified niche from the context_block>",
"core_audience_desire": "<The deep psychological need driving viewership — distinguish surface desire from core desire>"
}},
"proven_frameworks": [
{{
"angle": "<Named angle archetype, e.g., 'The Competence Exposé', 'The System Indictment', 'The Contrarian Validation'>",
"psychological_trigger": "<Precise psychological mechanism from the approved list or a newly defined one>",
"transcript_evidence": "<Direct quote or close paraphrase from the context_block that proves this angle is working>"
}}
],
"high_retention_hooks": [
{{
"hook_format": "<Structural formula only, e.g., '[Counterintuitive Outcome] achieved by [Unexpected Actor] despite [Assumed Barrier]'>",
"pattern_interrupt": "<What makes this hook cognitively disruptive in the first 1.5 seconds — be mechanistic, not subjective>",
"example": "<One highly specific, non-clichéd example generated using the formula above, tailored to the niche data>"
}}
],
"retention_mechanics": [
"<One structural technique with timing, sequencing, and mechanism detail — no vague observations>"
]
}}'''
    return prompt


def call_llm(prompt: str) -> str:
    """Call the configured LLM API with the given prompt.

    Uses either OpenAI, Anthropic, or OpenAI-compatible API based on configuration.

    Args:
        prompt: The prompt to send to the LLM.

    Returns:
        The raw response content from the LLM.

    Raises:
        ValueError: If LLM_PROVIDER is not set to a valid value.
    """
    provider = config.llm_provider

    if provider == "openai":
        client = _create_openai_client(config.openai_api_key)
        response = client.chat.completions.create(
            model=config.openai_model,
            temperature=0.7,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    elif provider == "anthropic":
        client = anthropic.Anthropic(api_key=config.anthropic_api_key)
        response = client.messages.create(
            model=config.anthropic_model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    elif provider == "openai_compatible":
        client = _create_openai_client(
            config.openai_api_key,
            config.openai_compatible_api_base,
        )
        response = client.chat.completions.create(
            model=config.openai_model,
            temperature=0.7,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    else:
        raise ValueError(
            f"Invalid LLM_PROVIDER: '{provider}'. Must be 'openai', 'anthropic', or 'openai_compatible'."
        )


def parse_and_validate(llm_response: str) -> dict[str, Any]:
    """Parse and validate the LLM JSON response.

    Attempts to parse the LLM response as JSON and validates that
    all required keys and structures are present.
    Handles non-structured output by extracting JSON from the response.

    Args:
        llm_response: The raw JSON string from the LLM.

    Returns:
        The parsed and validated dictionary.

    Raises:
        ValueError: If parsing or validation fails.
    """
    import re
    
    cleaned_response = llm_response.strip()
    
    json_match = re.search(r'\{[\s\S]*\}', cleaned_response)
    if json_match:
        cleaned_response = json_match.group(0)
    
    try:
        parsed = json.loads(cleaned_response)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse LLM JSON response: {e}")

    required_keys = ["niche_analysis", "proven_frameworks", "high_retention_hooks", "retention_mechanics"]
    for key in required_keys:
        if key not in parsed:
            raise ValueError(f"Missing required key in LLM response: {key}")

    if not isinstance(parsed["proven_frameworks"], list) or len(parsed["proven_frameworks"]) < 2:
        raise ValueError(
            f"proven_frameworks must be a list with at least 2 items, "
            f"got {len(parsed.get('proven_frameworks', []))}"
        )

    if not isinstance(parsed["high_retention_hooks"], list) or len(parsed["high_retention_hooks"]) < 2:
        raise ValueError(
            f"high_retention_hooks must be a list with at least 2 items, "
            f"got {len(parsed.get('high_retention_hooks', []))}"
        )
    
    if not isinstance(parsed["retention_mechanics"], list) or len(parsed["retention_mechanics"]) < 2:
        raise ValueError(
            f"retention_mechanics must be a list with at least 2 items, "
            f"got {len(parsed.get('retention_mechanics', []))}"
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