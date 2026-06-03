#!/usr/bin/env python3
"""Fetch B站 video lists via search API (alternative to space API when IP is rate-limited)."""

import json
import os
import random
import re
import string
import time

import httpx

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Referer": "https://search.bilibili.com",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

API_BASE = "https://api.bilibili.com"


def _random_buvid() -> str:
    return "XY" + "".join(random.choices(string.ascii_uppercase + string.digits, k=35))


def search_up_videos(keyword: str, up_mid: int, page: int = 1, ps: int = 42) -> dict:
    buvid = _random_buvid()
    client = httpx.Client(
        headers=HEADERS,
        cookies={"buvid3": buvid},
        timeout=30,
        follow_redirects=True,
    )
    params = {
        "search_type": "video",
        "keyword": keyword,
        "up_mid": str(up_mid),
        "order": "pubdate",
        "page": str(page),
        "pagesize": str(ps),
    }
    resp = client.get(f"{API_BASE}/x/web-interface/wbi/search/type", params=params)
    resp.raise_for_status()
    return resp.json()


def fetch_all_via_search(up_name: str, up_mid: int, max_pages: int = 15) -> list[dict]:
    all_videos = []
    seen_bvids = set()

    for page in range(1, max_pages + 1):
        time.sleep(3 + random.uniform(0, 2))
        try:
            data = search_up_videos(up_name, up_mid, page)
        except Exception as e:
            print(f"  Page {page}: error - {e}")
            break

        if data.get("code") != 0:
            print(f"  Page {page}: API error {data.get('code')} - {data.get('message', '')}")
            break

        results = data.get("data", {}).get("result", [])
        if not results:
            print(f"  Page {page}: no results")
            break

        new_count = 0
        for r in results:
            bvid = r.get("bvid", "")
            if bvid in seen_bvids:
                continue
            seen_bvids.add(bvid)
            tag_list = re.findall(r"<em class=\"keyword\">(.+?)</em>", r.get("tag", ""))
            all_videos.append({
                "bvid": bvid,
                "aid": r.get("aid", 0),
                "title": re.sub(r"<.*?>", "", r.get("title", "")),
                "description": re.sub(r"<.*?>", "", r.get("description", "")).strip(),
                "duration": r.get("duration", ""),
                "pubdate": r.get("pubdate", 0),
                "play": r.get("play", 0),
                "tags": tag_list,
            })
            new_count += 1

        print(f"  Page {page}: {new_count} new ({len(all_videos)} total)")

        if new_count == 0:
            break

    return all_videos


def main():
    up_list = [
        ("小约翰可汗", 23947287, "xiaoyuehan_videos.json"),
        ("王骁Albert", 52165725, "wangxiao_videos.json"),
    ]

    data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
    os.makedirs(data_dir, exist_ok=True)

    for up_name, up_mid, filename in up_list:
        print(f"\n{'='*50}")
        print(f"Searching videos for {up_name} (mid={up_mid})...")
        videos = fetch_all_via_search(up_name, up_mid)
        print(f"  Total: {len(videos)} videos")

        output = {
            "uid": up_mid,
            "name": up_name,
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "count": len(videos),
            "videos": videos,
            "source": "search_api",
        }
        path = os.path.join(data_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"  Saved to {path}")
        time.sleep(5)


if __name__ == "__main__":
    main()
