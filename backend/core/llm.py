import os
from typing import Dict, List

from fastapi import HTTPException
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    """Lazily create and return a configured OpenAI client."""
    global _client
    if _client is not None:
        return _client

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY is not set on the server.",
        )

    _client = OpenAI(api_key=api_key)
    return _client


def _format_history(conversation: List[dict]) -> List[Dict[str, str]]:
    """Normalize conversation history into OpenAI chat format."""
    formatted = []
    for msg in conversation:
        role = getattr(msg, "role", None) or (msg.get("role") if isinstance(msg, dict) else "user")
        content = getattr(msg, "message", None) or (msg.get("message") if isinstance(msg, dict) else "")
        formatted.append({"role": role or "user", "content": content})
    return formatted


def generate_placeholder_response(
    *,
    conversation: List[dict],
    placeholders: List[Dict],
    values: Dict[str, str],
    next_placeholder: Dict | None,
) -> str:
    """
    Ask OpenAI to produce the next assistant reply that keeps the same flow
    (ask for the next placeholder value or confirm completion).
    """
    client = _get_client()

    placeholder_names = [p["name"] for p in placeholders]
    filled_summary = "; ".join(f"[{k}]=`{v}`" for k, v in values.items()) or "none yet"

    system_prompt = (
        "You are a concise legal document assistant helping fill placeholder values in a DOCX template. "
        f"Placeholders to complete: {placeholder_names}. "
        f"Values already provided: {filled_summary}. "
        "Ask only one clear question at a time. "
        "If all placeholders are filled, simply confirm the document is ready."
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(_format_history(conversation))

    if next_placeholder:
        messages.append(
            {
                "role": "system",
                "content": (
                    f"Ask for the value of [{next_placeholder['name']}]. "
                    f"Prefer this wording: {next_placeholder.get('question', '')}"
                ),
            }
        )
    else:
        messages.append(
            {
                "role": "system",
                "content": "Everything is filled. Confirm completion briefly without adding new placeholders.",
            }
        )

    try:
        completion = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages,
            temperature=0.2,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"OpenAI request failed: {exc}") from exc

    return completion.choices[0].message.content.strip()
