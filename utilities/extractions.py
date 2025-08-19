import os
import re
import json
from bs4 import BeautifulSoup
from typing import List, Any, Set

URL_REGEX = re.compile(r"https?://[\w\-\.:%#\?\/=\+&@~\[\]]+", re.IGNORECASE)


def extract_urls_from_text(text: str) -> List[str]:
    return list(dict.fromkeys(m.group(0) for m in URL_REGEX.finditer(text)))


def extract_urls_from_json(obj: Any) -> Set[str]:
    urls: Set[str] = set()

    def walk(node: Any):
        if isinstance(node, dict):
            for k, v in node.items():
                if k in ("uri", "url") and isinstance(v, str) and URL_REGEX.match(v):
                    urls.add(v)
                walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, str):
            if URL_REGEX.match(node):
                urls.add(node)
    walk(obj)
    return urls


def extract_urls_from_file(path: str) -> List[str]:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")
    ext = os.path.splitext(path)[1].lower()
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        data = f.read()

    if ext in (".txt", ".log"):
        urls = [line.strip() for line in data.splitlines() if line.strip().startswith("http")]
        if not urls:
            urls = extract_urls_from_text(data)
        return list(dict.fromkeys(urls))
    elif ext == ".json":
        try:
            obj = json.loads(data)
        except json.JSONDecodeError:
            # fallback: regex in text
            return extract_urls_from_text(data)
        return sorted(extract_urls_from_json(obj))
    elif ext in (".html", ".htm", ".xml"):
        soup = BeautifulSoup(data, "lxml")
        urls: Set[str] = set()
        for tag in soup.find_all(href=True):
            href = tag.get("href")
            if href and href.startswith("http"):
                urls.add(href)
        for tag in soup.find_all(src=True):
            src = tag.get("src")
            if src and src.startswith("http"):
                urls.add(src)
        # Plus everything that looks like a URL in the text
        urls |= set(extract_urls_from_text(data))
        return sorted(urls)
    else:
        # generic fallback
        return extract_urls_from_text(data)
