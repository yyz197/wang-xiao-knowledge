#!/usr/bin/env python3
"""Build MOC (Map of Content) index pages by scanning all note frontmatter."""

import os
import re
import time
from collections import defaultdict

import frontmatter
import yaml

VAULT_ROOT = os.path.join(os.path.dirname(__file__), "..")
MOC_DIR = os.path.join(VAULT_ROOT, "00-主题索引")
SERIES_DIRS = [
    "01-奇葩小国", "02-神奇组织", "03-硬核狠人",
    "04-骁话一下", "05-王骁其他", "06-小王看世界",
]

TOPIC_ALIASES = {
    "冷战": ["冷战", "美苏", "铁幕", "柏林墙"],
    "非洲": ["非洲", "埃塞俄比亚", "刚果", "尼日利亚", "南非", "苏丹", "索马里"],
    "中东": ["中东", "伊朗", "伊拉克", "沙特", "以色列", "巴勒斯坦", "叙利亚"],
    "东南亚": ["东南亚", "越南", "柬埔寨", "缅甸", "泰国", "印尼"],
    "拉美": ["拉美", "拉丁美洲", "巴西", "阿根廷", "智利", "古巴", "墨西哥"],
    "欧洲": ["欧洲", "英国", "法国", "德国", "意大利", "西班牙"],
    "亚洲": ["亚洲", "中国", "日本", "韩国", "朝鲜", "印度", "巴基斯坦"],
    "国际关系": ["国际关系", "中美", "中俄", "一带一路", "外交", "联合国"],
    "经济": ["经济", "金融", "贸易", "投资", "GDP"],
    "军事": ["军事", "战争", "军队", "武器", "军备"],
    "殖民": ["殖民", "殖民地", "独立", "解放"],
    "政变": ["政变", "军事政变", "军政府", "独裁"],
    "间谍": ["间谍", "情报", "暗杀", "特工", "KGB", "CIA"],
    "资源": ["资源", "石油", "矿产", "钻石", "黄金"],
}


def normalize_topic(t: str) -> str:
    t_lower = t.lower().strip()
    for canonical, aliases in TOPIC_ALIASES.items():
        for alias in aliases:
            if alias.lower() in t_lower or t_lower in alias.lower():
                return canonical
    return t


def scan_notes():
    topic_notes = defaultdict(list)
    region_notes = defaultdict(list)
    country_notes = defaultdict(list)
    series_notes = defaultdict(list)

    for sdir in SERIES_DIRS:
        path = os.path.join(VAULT_ROOT, sdir)
        if not os.path.isdir(path):
            continue
        for fname in os.listdir(path):
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(path, fname)
            try:
                post = frontmatter.load(fpath)
            except Exception:
                continue

            data = post.metadata
            title = data.get("title", fname.replace(".md", ""))
            bvid = data.get("bv", "")
            series = data.get("series", sdir)
            country = data.get("country", "")
            region = data.get("region", "")
            topics = data.get("topic", [])
            related = data.get("related", [])

            note_ref = {
                "title": title,
                "file": f"{sdir}/{fname}",
                "bvid": bvid,
                "series": series,
                "country": country,
            }

            series_notes[series].append(note_ref)

            if country:
                country_notes[country].append(note_ref)

            if region:
                region_notes[region].append(note_ref)

            for t in topics:
                canonical = normalize_topic(t)
                note_ref_with_label = dict(note_ref)
                note_ref_with_label["topic_label"] = t
                seen = {(n["file"], n.get("topic_label", "")) for n in topic_notes[canonical]}
                if (note_ref_with_label["file"], t) not in seen:
                    topic_notes[canonical].append(note_ref_with_label)

    return topic_notes, region_notes, country_notes, series_notes


def build_breadcrumb(items: list[str]) -> str:
    crumbs = ["[[首页|首页]]"]
    for item in items:
        if item == "00-主题索引":
            crumbs.append("[[00-主题索引/主题索引|主题索引]]")
        else:
            crumbs.append(item)
    return " > ".join(crumbs)


def group_by_series(refs: list[dict]) -> dict[str, list[dict]]:
    grouped = defaultdict(list)
    for r in refs:
        grouped[r["series"]].append(r)
    return dict(grouped)


def build_moc_page(key: str, refs: list[dict], moc_type: str, parent_keys: list[str] | None = None) -> str:
    created = time.strftime("%Y-%m-%dT%H:%M:%S")
    breadcrumb = build_breadcrumb(["00-主题索引"] + (parent_keys or []))

    lines = ["---"]
    lines.append(f"created: {created}")
    lines.append(f"type: moc")
    lines.append(f"moc_type: {moc_type}")
    lines.append(f"title: {key}")
    lines.append("---")
    lines.append("")
    lines.append(breadcrumb)
    lines.append("")
    lines.append(f"# {key}")
    lines.append("")

    grouped = group_by_series(refs)
    series_order = [
        ("01-奇葩小国", "奇葩小国 — 小约翰可汗"),
        ("02-神奇组织", "神奇组织 — 小约翰可汗"),
        ("03-硬核狠人", "硬核狠人 — 小约翰可汗"),
        ("04-骁话一下", "骁话一下 — 王骁Albert"),
        ("05-王骁其他", "王骁其他 — 王骁Albert"),
        ("06-小王看世界", "小王看世界 — 王骁Albert"),
    ]

    total = 0
    for sdir, label in series_order:
        items = grouped.get(sdir, [])
        if not items:
            continue
        total += len(items)
        lines.append(f"## {label}（{len(items)} 篇）")
        lines.append("")
        for r in sorted(items, key=lambda x: x["title"]):
            extra = ""
            if r.get("country"):
                extra += f" [{r['country']}]"
            lines.append(f"- [[{r['file']}|{r['title']}]]{extra}")
        lines.append("")

    lines.append(f"> 共 {total} 篇笔记")
    return "\n".join(lines)


def clean_moc_dir():
    os.makedirs(MOC_DIR, exist_ok=True)
    for fname in os.listdir(MOC_DIR):
        if fname.endswith(".md") and fname != "主题索引.md":
            os.remove(os.path.join(MOC_DIR, fname))


def build_topic_index(topic_notes: dict, region_notes: dict, country_notes: dict) -> str:
    created = time.strftime("%Y-%m-%dT%H:%M:%S")
    lines = ["---"]
    lines.append(f"created: {created}")
    lines.append("type: moc")
    lines.append("title: 主题索引")
    lines.append("---")
    lines.append("")
    lines.append("[[首页|首页]] > 主题索引")
    lines.append("")
    lines.append("# 主题索引")
    lines.append("")

    if region_notes:
        lines.append("## 按地区")
        lines.append("")
        for k in sorted(region_notes.keys()):
            lines.append(f"- [[{k}|{k}]]（{len(region_notes[k])} 篇）")
        lines.append("")

    if country_notes:
        lines.append("## 按国家")
        lines.append("")
        for k in sorted(country_notes.keys()):
            lines.append(f"- [[{k}|{k}]]（{len(country_notes[k])} 篇）")
        lines.append("")

    if topic_notes:
        lines.append("## 按主题")
        lines.append("")
        for k in sorted(topic_notes.keys()):
            lines.append(f"- [[{k}|{k}]]（{len(topic_notes[k])} 篇）")
        lines.append("")

    return "\n".join(lines)


def main():
    print("Scanning notes...")
    topic_notes, region_notes, country_notes, series_notes = scan_notes()

    cleanup = True
    if cleanup:
        print("Cleaning existing MOC pages...")
        clean_moc_dir()

    print(f"Building MOC pages:")
    print(f"  Topics: {len(topic_notes)}")

    for key, refs in topic_notes.items():
        content = build_moc_page(key, refs, "topic")
        safe_name = key.replace("/", "-").replace("\\", "-")
        out_path = os.path.join(MOC_DIR, f"{safe_name}.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

    for key, refs in region_notes.items():
        content = build_moc_page(key, refs, "region")
        safe_name = key.replace("/", "-").replace("\\", "-")
        out_path = os.path.join(MOC_DIR, f"{safe_name}.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

    for key, refs in country_notes.items():
        content = build_moc_page(key, refs, "country")
        safe_name = key.replace("/", "-").replace("\\", "-")
        out_path = os.path.join(MOC_DIR, f"{safe_name}.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

    index_content = build_topic_index(topic_notes, region_notes, country_notes)
    with open(os.path.join(MOC_DIR, "主题索引.md"), "w", encoding="utf-8") as f:
        f.write(index_content)

    print(f"  Regions: {len(region_notes)}")
    print(f"  Countries: {len(country_notes)}")
    print(f"  Total MOC pages: {len(topic_notes) + len(region_notes) + len(country_notes) + 1}")
    print("Done.")


if __name__ == "__main__":
    main()
