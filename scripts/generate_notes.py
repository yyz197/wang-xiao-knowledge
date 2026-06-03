#!/usr/bin/env python3
"""Generate Obsidian notes from B站 video metadata and subtitles using DeepSeek V4."""

import json
import os
import re
import time
from collections import Counter

from openai import OpenAI

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SUBS_DIR = os.path.join(DATA_DIR, "subtitles")
RAW_DIR = os.path.join(DATA_DIR, "raw")
VAULT_ROOT = os.path.join(os.path.dirname(__file__), "..")

SYSTEM_PROMPT = """你是一个知识管理助手。你将收到一个 B 站视频的字幕文本，请将其整理为结构化的 Obsidian 笔记。

返回格式（严格 JSON，不要 markdown 代码块包裹）：
{
  "title": "笔记标题（保留原标题，可适当精简）",
  "summary": "200字以内的内容摘要",
  "key_points": ["要点1", "要点2", "要点3"],
  "timeline": ["事件1", "事件2"],
  "entities": {
    "countries": ["国家名1", "国家名2"],
    "people": ["人名1", "人名2"],
    "organizations": ["组织名1", "组织名2"],
    "events": ["事件名1"]
  },
  "topics": ["主题标签1", "主题标签2"],
  "region": "地区（非洲/欧洲/亚洲/中东/拉美/北美/全球）",
  "category": "分类（历史/时政/经济/军事/社会/人物/组织/科技）"
}

规则：
1. entities 和 topics 中的每个值尽量不超过10个字
2. region 从给定的选项中选择一个
3. 如果字幕不足100字或质量太差无法提炼，返回 {"error": "insufficient_content"}\n"""

USER_PROMPT_TEMPLATE = """请整理以下视频内容的笔记。

视频标题：{title}
视频简介：{description}
B站标签：{tags}

字幕内容：
{subtitle_text}"""


def load_env():
    env_path = os.path.join(VAULT_ROOT, ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    os.environ.setdefault(key, val)


def classify_series(video: dict, up_name: str) -> str:
    tags = [t.lower() for t in video.get("tags", [])]
    title = video.get("title", "").lower()
    tag_str = " ".join(tags)
    title_str = f"{title} {tag_str}"

    if up_name == "小约翰可汗":
        if "奇葩小国" in title_str or "小国" in title_str:
            return "01-奇葩小国"
        if "神奇组织" in title_str or "组织" in title_str:
            return "02-神奇组织"
        if "硬核狠人" in title_str or "狠人" in title_str:
            return "03-硬核狠人"
        return "01-奇葩小国"

    if up_name == "王骁Albert":
        if "骁话一下" in title_str:
            return "04-骁话一下"
        if "小王" in title_str or "看世界" in title_str:
            return "06-小王看世界"
        return "05-王骁其他"

    return "05-王骁其他"


def extract_country(title: str, entities: dict) -> str:
    countries = entities.get("countries", [])
    if countries:
        return countries[0]
    return ""


def call_deepseek(client: OpenAI, title: str, description: str, tags: list[str], subtitle_text: str) -> dict:
    prompt = USER_PROMPT_TEMPLATE.format(
        title=title,
        description=description[:500],
        tags=", ".join(tags) if tags else "无",
        subtitle_text=subtitle_text[:8000],
    )
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=4096,
        response_format={"type": "json_object"},
    )
    content = resp.choices[0].message.content
    return json.loads(content)


def build_frontmatter(video: dict, series: str, entities: dict, topics: list[str], region: str, title: str) -> str:
    created = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(video.get("pubdate", time.time())))
    country = extract_country(video.get("title", ""), entities)
    source = "[[小约翰可汗]]" if series.startswith("01") or series.startswith("02") or series.startswith("03") else "[[王骁Albert]]"
    combined_topics = list(dict.fromkeys(topics + (entities.get("topics", []))))

    related = []
    related.extend(entities.get("countries", []))
    related.extend(entities.get("people", []))
    related.extend(entities.get("organizations", []))
    related.extend(entities.get("events", []))
    related.extend(combined_topics)
    related = list(dict.fromkeys(related))[:15]

    lines = ["---"]
    lines.append(f"title: \"{title}\"")
    lines.append(f"created: {created}")
    lines.append(f"category: {entities.get('category', '未分类')}")
    lines.append(f"source: \"{source}\"")
    lines.append(f"series: \"{series}\"")
    lines.append(f"bv: {video['bvid']}")
    if country:
        lines.append(f"country: {country}")
    if region:
        lines.append(f"region: {region}")
    if combined_topics:
        lines.append("topic:")
        for t in combined_topics[:5]:
            lines.append(f"  - {t}")
    if related:
        lines.append("related:")
        for r in related:
            lines.append(f"  - {r}")
    lines.append("---")
    return "\n".join(lines)


def build_note(video: dict, series: str, analysis: dict) -> str:
    title = analysis.get("title", video.get("title", "未命名"))
    parts = [build_frontmatter(video, series, analysis.get("entities", {}),
                                analysis.get("topics", []), analysis.get("region", ""), title)]
    parts.append("")
    parts.append(f"# {title}")
    parts.append("")
    parts.append(f"> 原视频：[BV{video['bvid']}](https://www.bilibili.com/video/{video['bvid']})")
    parts.append("")

    summary = analysis.get("summary", "")
    if summary:
        parts.append("## 摘要")
        parts.append("")
        parts.append(summary)
        parts.append("")

    key_points = analysis.get("key_points", [])
    if key_points:
        parts.append("## 关键信息")
        parts.append("")
        for p in key_points:
            parts.append(f"- {p}")
        parts.append("")

    timeline = analysis.get("timeline", [])
    if timeline:
        parts.append("## 时间线")
        parts.append("")
        for t in timeline:
            parts.append(f"- {t}")
        parts.append("")

    entities = analysis.get("entities", {})
    if entities:
        parts.append("## 相关实体")
        parts.append("")
        for label, key in [("国家", "countries"), ("人物", "people"), ("组织", "organizations"), ("事件", "events")]:
            items = entities.get(key, [])
            if items:
                parts.append(f"- **{label}**：{'、'.join(items)}")
        parts.append("")

    related = list(dict.fromkeys(
        entities.get("countries", []) +
        entities.get("people", []) +
        entities.get("organizations", []) +
        entities.get("events", []) +
        analysis.get("topics", [])
    ))[:10]
    if related:
        parts.append("## 相关笔记")
        parts.append("")
        for r in related:
            parts.append(f"- [[{r}]]")
        parts.append("")

    return "\n".join(parts)


def process_videos(up_name: str, videos_json: str, limit: int | None = None):
    with open(videos_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    videos = data["videos"]
    if limit:
        videos = videos[:limit]

    subs_dir = os.path.join(SUBS_DIR, up_name)
    load_env()

    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

    if not api_key:
        print(f"ERROR: DEEPSEEK_API_KEY not set in .env")
        return

    client = OpenAI(api_key=api_key, base_url=base_url)
    total = len(videos)
    success = 0
    no_sub = 0
    no_content = 0

    for i, v in enumerate(videos):
        bvid = v["bvid"]
        series = classify_series(v, up_name)
        out_dir = os.path.join(VAULT_ROOT, series)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"{bvid}.md")

        if os.path.exists(out_path):
            success += 1
            if (i + 1) % 20 == 0:
                print(f"  [{up_name}] {i+1}/{total} (skipped existing, {success} ok)")
            continue

        sub_path = os.path.join(subs_dir, f"{bvid}.txt")
        if not os.path.exists(sub_path) or os.path.getsize(sub_path) < 50:
            no_sub += 1
            continue

        with open(sub_path, "r", encoding="utf-8") as f:
            subtitle_text = f.read()

        try:
            analysis = call_deepseek(client, v.get("title", ""), v.get("description", ""),
                                     v.get("tags", []), subtitle_text)
        except Exception as e:
            print(f"  [{up_name}] {i+1}/{total} {bvid}: DeepSeek error - {e}")
            time.sleep(2)
            continue

        if "error" in analysis:
            no_content += 1
            if (i + 1) % 10 == 0:
                print(f"  [{up_name}] {i+1}/{total} ({success} notes, {no_content} no content)")
            continue

        note = build_note(v, series, analysis)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(note)
        success += 1

        if (i + 1) % 10 == 0:
            print(f"  [{up_name}] {i+1}/{total} ({success} notes, {no_content} no content, {no_sub} no subs)")

        time.sleep(0.5)

    print(f"  [{up_name}] Done: {success} notes, {no_content} no content, {no_sub} no subtitles")


def main():
    configs = [
        ("小约翰可汗", "xiaoyuehan_videos.json"),
        ("王骁Albert", "wangxiao_videos.json"),
    ]
    for name, filename in configs:
        path = os.path.join(RAW_DIR, filename)
        if not os.path.exists(path):
            print(f"Skipping {name}: {filename} not found")
            continue
        print(f"\nGenerating notes for {name}...")
        process_videos(name, path)


if __name__ == "__main__":
    main()
