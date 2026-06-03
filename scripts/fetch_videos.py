#!/usr/bin/env python3
"""Fetch all videos from B站 UP主 using space API with WBI signing.

If you encounter "风控校验失败" (-352), try:
  1. Set HTTP_PROXY env var to use a proxy
  2. Wait 10+ minutes between retries
  3. Run from a different network/IP
"""

import hashlib
import json
import os
import random
import string
import time
import urllib.parse
from typing import Any

import httpx

MIXIN_KEY_ENC_TAB = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35,
    27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13,
    37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4,
    22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 52, 44, 34,
]

API_BASE = "https://api.bilibili.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
}


def _random_buvid() -> str:
    return "XY" + "".join(random.choices(string.ascii_uppercase + string.digits, k=35))


def _build_client() -> httpx.Client:
    buvid = _random_buvid()
    proxy = os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY") or None
    return httpx.Client(
        headers=HEADERS,
        cookies={"buvid3": buvid, "buvid4": buvid},
        proxy=proxy,
        timeout=30,
        follow_redirects=True,
    )


def get_mixin_key(raw_key: str) -> str:
    return "".join(raw_key[i] for i in MIXIN_KEY_ENC_TAB)[:32]


def fetch_nav_keys(client: httpx.Client) -> tuple[str, str]:
    resp = client.get(f"{API_BASE}/x/web-interface/nav")
    resp.raise_for_status()
    wbi = resp.json()["data"]["wbi_img"]
    img_key = wbi["img_url"].split("/")[-1].replace(".png", "")
    sub_key = wbi["sub_url"].split("/")[-1].replace(".png", "")
    return img_key, sub_key


def sign_params(params: dict, img_key: str, sub_key: str) -> dict:
    mixin_key = get_mixin_key(img_key + sub_key)
    params["wts"] = int(time.time())
    params = dict(sorted(params.items()))
    query = urllib.parse.urlencode(params)
    w_rid = hashlib.md5((query + mixin_key).encode()).hexdigest()
    params["w_rid"] = w_rid
    return params


def fetch_videos(uid: int, max_pages: int = 50) -> list[dict]:
    all_videos = []
    consecutive_empty = 0

    for attempt in range(5):
        client = _build_client()
        try:
            img_key, sub_key = fetch_nav_keys(client)
            break
        except Exception as e:
            print(f"  Nav fetch attempt {attempt+1} failed: {e}")
            time.sleep(3)
    else:
        print("  Failed to fetch WBI keys")
        return all_videos

    for page in range(1, max_pages + 1):
        params = {"mid": str(uid), "ps": "50", "pn": str(page), "order": "pubdate"}
        params = sign_params(params, img_key, sub_key)

        for retry in range(5):
            try:
                resp = client.get(f"{API_BASE}/x/space/wbi/arc/search", params=params)
                data = resp.json()

                if data["code"] in (-799, -352) or "频繁" in data.get("message", "") or "风控" in data.get("message", ""):
                    wait = (2 ** retry) * 2 + random.uniform(0, 2)
                    print(f"    Rate limited, waiting {wait:.1f}s...")
                    time.sleep(wait)
                    continue

                if data["code"] != 0:
                    print(f"  API error (code {data['code']}): {data['message']}")
                    if page == 1:
                        return all_videos
                    break

                vlist = data["data"]["list"]["vlist"]
                if not vlist:
                    consecutive_empty += 1
                    if consecutive_empty >= 2:
                        return all_videos
                    break

                consecutive_empty = 0
                for v in vlist:
                    all_videos.append({
                        "bvid": v["bvid"],
                        "aid": v["aid"],
                        "title": v["title"],
                        "description": v.get("description", "").strip(),
                        "duration": v.get("length", ""),
                        "pubdate": v["created"],
                        "play": v.get("play", 0),
                        "comment": v.get("comment", 0),
                        "series": v.get("meta", {}).get("title", ""),
                        "series_id": v.get("meta", {}).get("id", 0),
                        "ep_count": v.get("meta", {}).get("ep_count", 0),
                    })

                print(f"  Page {page}, got {len(vlist)} videos (total: {len(all_videos)})")
                break

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 412:
                    print(f"  HTTP 412 on page {page}, stopping.")
                    return all_videos
                wait = (2 ** retry) + random.uniform(0, 1)
                time.sleep(wait)
        else:
            print(f"  Failed after 5 retries on page {page}")
            return all_videos

        delay = 5 + random.uniform(0, 3)
        time.sleep(delay)

    return all_videos


def fetch_tags(bvid: str, client: httpx.Client) -> list[str]:
    try:
        resp = client.get(f"{API_BASE}/x/tag/archive/tags", params={"bvid": bvid})
        resp.raise_for_status()
        data = resp.json()
        if data["code"] != 0:
            return []
        return [t["tag_name"] for t in data["data"]]
    except Exception:
        return []


def main():
    up_list = [
        {"uid": 23947287, "name": "小约翰可汗", "file": "xiaoyuehan_videos.json"},
        {"uid": 52165725, "name": "王骁Albert", "file": "wangxiao_videos.json"},
    ]

    data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
    os.makedirs(data_dir, exist_ok=True)

    for up in up_list:
        print(f"\n{'='*50}")
        print(f"Fetching videos for {up['name']} (UID: {up['uid']})...")
        videos = fetch_videos(up["uid"])
        print(f"  Total: {len(videos)} videos")

        if not videos:
            output = {
                "uid": up["uid"],
                "name": up["name"],
                "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "count": 0,
                "videos": [],
                "error": "Failed to fetch",
            }
            path = os.path.join(data_dir, up["file"])
            with open(path, "w", encoding="utf-8") as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            print(f"  Saved empty result to {path}")
            continue

        print("  Fetching tags (batch sample)...")
        tag_client = _build_client()
        for i, v in enumerate(videos):
            try:
                tags = fetch_tags(v["bvid"], tag_client)
                v["tags"] = tags
            except Exception:
                v["tags"] = []
            if (i + 1) % 20 == 0:
                print(f"    {i+1}/{len(videos)} tags fetched")
            time.sleep(0.5)

        output = {
            "uid": up["uid"],
            "name": up["name"],
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "count": len(videos),
            "videos": videos,
        }
        path = os.path.join(data_dir, up["file"])
        with open(path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"  Saved to {path}")

        time.sleep(10)


if __name__ == "__main__":
    main()
