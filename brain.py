import json
import os
from openai import OpenAI

from prompts import IDENTITY, CYCLE_PROMPT


def think(feed_items, memories):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    model = os.environ.get("OPENAI_MODEL", "gpt-5.6")

    payload = {
        "recent_memory": memories,
        "feed": feed_items,
    }

    response = client.responses.create(
        model=model,
        instructions=IDENTITY,
        input=CYCLE_PROMPT + "\n\nDATA:\n" + json.dumps(payload, ensure_ascii=False),
        text={
            "format": {
                "type": "json_schema",
                "name": "agentb_cycle",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "analysis": {"type": "string"},
                        "novelty": {"type": "string"},
                        "questions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 1,
                            "maxItems": 3
                        },
                        "action": {
                            "type": "string",
                            "enum": ["none", "post", "comment"]
                        },
                        "target_post_id": {"type": ["string", "null"]},
                        "title": {"type": ["string", "null"]},
                        "content": {"type": ["string", "null"]}
                    },
                    "required": [
                        "summary", "analysis", "novelty", "questions",
                        "action", "target_post_id", "title", "content"
                    ],
                    "additionalProperties": False
                }
            }
        }
    )

    return json.loads(response.output_text)
