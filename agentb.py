import argparse
import json
import os
from dotenv import load_dotenv

from brain import think
from memory import append_memory, load_recent
from moltbook import MoltbookClient

load_dotenv()


def _extract_feed_items(payload):
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict):
        items = payload.get("posts") or payload.get("items") or payload.get("feed") or []
    else:
        items = []

    cleaned = []
    for item in items:
        if not isinstance(item, dict):
            continue
        author = item.get("author")
        if isinstance(author, dict):
            author = author.get("name") or author.get("username") or author.get("handle")
        cleaned.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "content": item.get("content") or item.get("body") or item.get("text"),
            "author": author,
            "submolt": item.get("submolt") or item.get("community"),
            "created_at": item.get("created_at"),
        })
    return cleaned


def cmd_feed(args):
    client = MoltbookClient()
    data = client.get_feed(limit=args.limit)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_memory(args):
    print(json.dumps(load_recent(args.limit), indent=2, ensure_ascii=False))


def cmd_cycle(args):
    client = MoltbookClient()
    feed_payload = client.get_feed(limit=args.limit)
    feed_items = _extract_feed_items(feed_payload)
    memories = load_recent()

    if not feed_items:
        raise RuntimeError("No feed items were returned; refusing to invent input.")

    result = think(feed_items, memories)

    public_result = None
    action = result.get("action", "none")
    if action == "post" and client.write_enabled:
        title = (result.get("title") or "AgentB research note").strip()
        content = (result.get("content") or "").strip()
        if content:
            public_result = client.create_post(args.submolt, title, content)
    elif action == "comment" and client.write_enabled:
        post_id = result.get("target_post_id")
        content = (result.get("content") or "").strip()
        if post_id and content:
            public_result = client.create_comment(post_id, content)

    record = append_memory({
        "feed_item_count": len(feed_items),
        "research": result,
        "published": bool(public_result),
        "publication_result": public_result,
    })

    print(json.dumps(record, indent=2, ensure_ascii=False))
    if action in {"post", "comment"} and not client.write_enabled:
        print("\nDraft produced, but external writes are disabled.")


def cmd_owner_email(args):
    client = MoltbookClient()
    result = client.setup_owner_email(args.email)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def build_parser():
    parser = argparse.ArgumentParser(description="AgentB persistent AI research agent")
    sub = parser.add_subparsers(dest="command", required=True)

    p_feed = sub.add_parser("feed", help="Read Moltbook feed")
    p_feed.add_argument("--limit", type=int, default=int(os.environ.get("FEED_LIMIT", "20")))
    p_feed.set_defaults(func=cmd_feed)

    p_cycle = sub.add_parser("cycle", help="Run one research cycle")
    p_cycle.add_argument("--limit", type=int, default=int(os.environ.get("FEED_LIMIT", "20")))
    p_cycle.add_argument("--submolt", default="agents")
    p_cycle.set_defaults(func=cmd_cycle)

    p_memory = sub.add_parser("memory", help="Show recent research memory")
    p_memory.add_argument("--limit", type=int, default=12)
    p_memory.set_defaults(func=cmd_memory)

    p_email = sub.add_parser("owner-email", help="Set Moltbook owner email after registration")
    p_email.add_argument("email")
    p_email.set_defaults(func=cmd_owner_email)

    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    args.func(args)
