import json
from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

client = Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """Чи бол мэргэжлийн сэтгүүлч-орчуулагч. Англи мэдээг монгол хэл рүү
байгалийн, ойлгомжтой, FB хуудсанд тохиромжтой байдлаар орчуулна.

Дүрэм:
- Гарчгийг сэтгэл татам, богино (80 тэмдэгтээс бага) болгоно
- Биеийн текстийг 2-4 богино параграф болгож хураангуйлна
- Мэдээний гол баримтыг гуйвуулахгүй
- 3-5 холбогдох hashtag нэмнэ (#мэдээ #дэлхий гэх мэт)
- Эх сурвалжийг доор нь дурдана

Хариултаа доорх JSON форматаар буцаана:
{
  "title": "...",
  "body": "...",
  "hashtags": ["#tag1", "#tag2"]
}"""


def translate_article(title: str, body: str, source_name: str, source_url: str) -> dict:
    user_msg = f"""Эх гарчиг: {title}

Эх мэдээ:
{body}

Эх сурвалж: {source_name}
Холбоос: {source_url}

JSON хариултыг буцаа."""

    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )

    text = resp.content[0].text.strip()
    # Extract JSON block if wrapped in code fences
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {"title": title, "body": text, "hashtags": []}

    return {
        "title": data.get("title", title),
        "body": data.get("body", ""),
        "hashtags": data.get("hashtags", []),
    }


def format_fb_post(translated: dict, source_name: str, source_url: str) -> str:
    parts = [
        translated["title"],
        "",
        translated["body"],
        "",
        f"Эх сурвалж: {source_name}",
        source_url,
    ]
    if translated.get("hashtags"):
        parts.append("")
        parts.append(" ".join(translated["hashtags"]))
    return "\n".join(parts)
