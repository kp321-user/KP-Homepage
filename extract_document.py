"""
extract_document.py — Extract structured data from document images using Claude's vision API.

Usage (CLI):
    python extract_document.py image.png
    python extract_document.py image.png --prompt "Extract all dates and names"
    python extract_document.py image.png --json

Usage (import):
    from extract_document import extract_from_file, extract_from_url
    data = extract_from_file("invoice.jpg", prompt="Extract line items and totals")
"""

import anthropic
import base64
import io
import json
import mimetypes
import sys
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image

load_dotenv()


SUPPORTED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}

DEFAULT_PROMPT = (
    "Extract all information from this document image. "
    "Include text, numbers, dates, names, addresses, and any structured data like tables. "
    "Organize the output clearly."
)

STRUCTURED_PROMPT = (
    "Extract all information from this document image and return it as JSON. "
    "Include all text, numbers, dates, names, and structured data. "
    "Use descriptive keys. Return only valid JSON with no surrounding text."
)


# API checks base64-encoded size; 10MB base64 ≈ 7.5MB raw
MAX_B64_BYTES = 10 * 1024 * 1024


def _encode_image(path: str) -> tuple[str, str]:
    """Return (base64_data, media_type) for a local image file, resizing if encoded size exceeds 10MB."""
    path = Path(path)
    media_type, _ = mimetypes.guess_type(str(path))
    if media_type not in SUPPORTED_TYPES:
        raise ValueError(f"Unsupported file type: {media_type}. Supported: {SUPPORTED_TYPES}")

    raw = path.read_bytes()
    encoded = base64.standard_b64encode(raw).decode("utf-8")
    if len(encoded) <= MAX_B64_BYTES:
        return encoded, media_type

    # Re-encode at reduced size until base64 fits under 10MB
    img = Image.open(io.BytesIO(raw))
    fmt = "JPEG" if media_type == "image/jpeg" else "PNG"
    scale = 0.85
    while scale > 0.1:
        buf = io.BytesIO()
        w, h = img.size
        img.resize((int(w * scale), int(h * scale)), Image.LANCZOS).save(buf, format=fmt, quality=85)
        encoded = base64.standard_b64encode(buf.getvalue()).decode("utf-8")
        if len(encoded) <= MAX_B64_BYTES:
            print(f"[resized to {scale:.0%} — {len(encoded)//1024}KB base64]", file=sys.stderr)
            return encoded, media_type
        scale -= 0.1
    raise ValueError("Could not reduce image to under 10MB even at minimum scale.")


def extract_from_file(
    image_path: str,
    prompt: str = DEFAULT_PROMPT,
    as_json: bool = False,
) -> str:
    """Extract data from a local image file using Claude's vision API."""
    client = anthropic.Anthropic()
    image_data, media_type = _encode_image(image_path)

    effective_prompt = STRUCTURED_PROMPT if as_json else prompt

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=4096,
        thinking={"type": "adaptive"},
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {"type": "text", "text": effective_prompt},
                ],
            }
        ],
    )

    return next(b.text for b in response.content if b.type == "text")


def extract_from_url(
    image_url: str,
    prompt: str = DEFAULT_PROMPT,
    as_json: bool = False,
) -> str:
    """Extract data from an image URL using Claude's vision API."""
    client = anthropic.Anthropic()
    effective_prompt = STRUCTURED_PROMPT if as_json else prompt

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=4096,
        thinking={"type": "adaptive"},
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "url",
                            "url": image_url,
                        },
                    },
                    {"type": "text", "text": effective_prompt},
                ],
            }
        ],
    )

    return next(b.text for b in response.content if b.type == "text")


def extract_from_multiple(
    image_paths: list[str],
    prompt: str = "Extract and summarize all information from these document images.",
    as_json: bool = False,
) -> str:
    """Extract data from multiple images in a single API call."""
    client = anthropic.Anthropic()
    effective_prompt = STRUCTURED_PROMPT if as_json else prompt

    content = []
    for path in image_paths:
        image_data, media_type = _encode_image(path)
        content.append(
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": image_data,
                },
            }
        )
    content.append({"type": "text", "text": effective_prompt})

    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=8192,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": content}],
    )

    return next(b.text for b in response.content if b.type == "text")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract data from document images using Claude.")
    parser.add_argument("image", help="Path to image file or URL")
    parser.add_argument("--prompt", "-p", default=None, help="Custom extraction prompt")
    parser.add_argument("--json", "-j", action="store_true", dest="as_json", help="Return structured JSON output")
    args = parser.parse_args()

    prompt = args.prompt or (STRUCTURED_PROMPT if args.as_json else DEFAULT_PROMPT)

    if args.image.startswith("http://") or args.image.startswith("https://"):
        result = extract_from_url(args.image, prompt=prompt, as_json=args.as_json)
    else:
        result = extract_from_file(args.image, prompt=prompt, as_json=args.as_json)

    # Strip markdown code fences if present
    text = result.strip()
    if text.startswith("```"):
        text = "\n".join(text.split("\n")[1:])
    if text.endswith("```"):
        text = "\n".join(text.split("\n")[:-1])
    text = text.strip()

    out = sys.stdout.buffer if hasattr(sys.stdout, "buffer") else sys.stdout
    if args.as_json:
        try:
            parsed = json.loads(text)
            out.write((json.dumps(parsed, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
        except json.JSONDecodeError:
            out.write((text + "\n").encode("utf-8"))
    else:
        out.write((text + "\n").encode("utf-8"))
