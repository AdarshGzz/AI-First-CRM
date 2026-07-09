"""
Robust JSON parsing utility for LLM outputs.
Extracts valid JSON dictionaries or lists even when surrounded by conversational text.
"""

import json


def extract_json(text: str) -> dict | list:
    """
    Extract the first valid JSON object or list from a string.
    Supports markdown code blocks and character-by-character brace matching.
    """
    if not text:
        return {}

    text_stripped = text.strip()

    # 1. Try simple direct load first
    try:
        return json.loads(text_stripped)
    except json.JSONDecodeError:
        pass

    # 2. Extract from markdown code blocks
    if "```" in text_stripped:
        parts = text_stripped.split("```")
        for part in parts:
            part = part.strip()
            # Strip language specifier
            if part.startswith("json"):
                part = part[4:].strip()
            elif part.startswith("javascript") or part.startswith("js"):
                part = part[10:].strip()
            
            if (part.startswith("{") and part.endswith("}")) or (part.startswith("[") and part.endswith("]")):
                try:
                    return json.loads(part)
                except json.JSONDecodeError:
                    pass

    # 3. Scan matching braces/brackets char-by-char
    for start_char, end_char in [("{", "}"), ("[", "]")]:
        start_idx = text_stripped.find(start_char)
        while start_idx != -1:
            brace_count = 0
            for i in range(start_idx, len(text_stripped)):
                if text_stripped[i] == start_char:
                    brace_count += 1
                elif text_stripped[i] == end_char:
                    brace_count -= 1
                    if brace_count == 0:
                        candidate = text_stripped[start_idx:i+1]
                        try:
                            return json.loads(candidate)
                        except json.JSONDecodeError:
                            break  # Try next start_idx
            start_idx = text_stripped.find(start_char, start_idx + 1)

    # 4. Fallback: simple substring between first and last marker
    for start_char, end_char in [("{", "}"), ("[", "]")]:
        start = text_stripped.find(start_char)
        end = text_stripped.rfind(end_char) + 1
        if start != -1 and end > start:
            try:
                return json.loads(text_stripped[start:end])
            except json.JSONDecodeError:
                pass

    # Default fallback empty types
    return [] if text_stripped.startswith("[") else {}
