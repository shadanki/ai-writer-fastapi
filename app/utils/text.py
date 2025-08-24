import datetime as dt

def front_matter(title: str, description: str, tags: list[str], lang: str = "ja") -> str:
    iso = dt.datetime.now(dt.timezone.utc).isoformat()
    tags_str = ", ".join([f'"{t}"' for t in tags])
    return (
        f"---\n"
        f"title: \"{title}\"\n"
        f"description: \"{description}\"\n"
        f"tags: [{tags_str}]\n"
        f"date: \"{iso}\"\n"
        f"lang: \"{lang}\"\n"
        f"canonical_url: \"\"\n"
        f"---\n\n"
    )