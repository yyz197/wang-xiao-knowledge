#!/usr/bin/env python3
"""Download and clean B站 video subtitles (CC + AI subtitles)."""

import json
import os
import time

import httpx

API_BASE = "https://api.bilibili.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": "https://www.bilibili.com",
}


def get_subtitle_urls(bvid: str, cid: int, client: httpx.Client) -> list[str]:
    resp = client.get(f"{API_BASE}/x/player/v2", params={"bvid": bvid, "cid": str(cid)})
    resp.raise_for_status()
    data = resp.json()
    if data["code"] != 0:
        return []
    info = data.get("data", {})
    sub_list = info.get("subtitle", {}).get("subtitles", [])
    urls = [s["subtitle_url"] for s in sub_list if s.get("subtitle_url")]
    return urls


def download_subtitle(url: str, client: httpx.Client) -> list[dict] | None:
    if url.startswith("//"):
        url = "https:" + url
    resp = client.get(url)
    resp.raise_for_status()
    data = resp.json()
    return data.get("body", [])


def subtitle_to_text(segments: list[dict]) -> str:
    lines = []
    for seg in segments:
        content = seg.get("content", "").strip()
        if content:
            lines.append(content)
    text = "\n".join(lines)
    text = "\n".join(dict.fromkeys(text.split("\n")))
    return text


def process_videos(videos_json_path: str, output_dir: str, max_count: int | None = None):
    with open(videos_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    videos = data["videos"]
    if max_count:
        videos = videos[:max_count]

    os.makedirs(output_dir, exist_ok=True)
    name = data["name"]
    total = len(videos)
    success = 0
    skipped = 0

    with httpx.Client(headers=HEADERS, timeout=30, follow_redirects=True) as client:
        for i, v in enumerate(videos):
            bvid = v["bvid"]
            cid = v.get("cid", 0)
            out_path = os.path.join(output_dir, f"{bvid}.txt")

            if os.path.exists(out_path) and os.path.getsize(out_path) > 50:
                success += 1
                skipped += 1
                if (i + 1) % 20 == 0:
                    print(f"  [{name}] {i+1}/{total} (skipped existing, {success} ok)")
                continue

            try:
                urls = get_subtitle_urls(bvid, cid, client)
                if not urls:
                    print(f"  [{name}] {i+1}/{total} {bvid}: no subtitles found")
                    continue

                all_segments = []
                for url in urls:
                    segments = download_subtitle(url, client)
                    if segments:
                        all_segments.extend(segments)

                if all_segments:
                    text = subtitle_to_text(all_segments)
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(text)
                    success += 1
                else:
                    print(f"  [{name}] {i+1}/{total} {bvid}: empty subtitle data")

            except Exception as e:
                print(f"  [{name}] {i+1}/{total} {bvid}: error - {e}")

            if (i + 1) % 20 == 0:
                print(f"  [{name}] {i+1}/{total} ({success} ok)")

            time.sleep(0.3)

    print(f"  [{name}] Done: {success}/{total} videos with subtitles ({skipped} skipped)")


def main():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
    subs_dir = os.path.join(os.path.dirname(__file__), "..", "data", "subtitles")

    up_configs = [
        ("xiaoyuehan_videos.json", "小约翰可汗"),
        ("wangxiao_videos.json", "王骁Albert"),
    ]

    for filename, name in up_configs:
        path = os.path.join(data_dir, filename)
        if not os.path.exists(path):
            print(f"Skipping {name}: {filename} not found (run fetch_videos.py first)")
            continue
        out_dir = os.path.join(subs_dir, name)
        print(f"\nProcessing {name}...")
        process_videos(path, out_dir)


if __name__ == "__main__":
    main()
