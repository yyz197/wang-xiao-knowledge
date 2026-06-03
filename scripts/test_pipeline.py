#!/usr/bin/env python3
"""Integration test: creates mock data and validates full pipeline."""

import json
import os
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

import generate_notes
import build_mocs

MOCK_VIDEOS_XIAOYUEHAN = {
    "uid": 23947287,
    "name": "小约翰可汗",
    "fetched_at": "2026-06-03T12:00:00",
    "count": 5,
    "videos": [
        {
            "bvid": "BV1Uy4y1S7Eq",
            "aid": 100001,
            "title": "阿尔巴尼亚：碉堡之国",
            "description": "阿尔巴尼亚的历史故事",
            "duration": "25:00",
            "pubdate": 1617235200,
            "play": 5000000,
            "comment": 50000,
            "series": "奇葩小国",
            "tags": ["奇葩小国", "历史", "阿尔巴尼亚", "冷战"],
        },
        {
            "bvid": "BV1a4411o001",
            "aid": 100002,
            "title": "刚果金的资源诅咒",
            "description": "刚果民主共和国的故事",
            "duration": "30:00",
            "pubdate": 1620000000,
            "play": 4000000,
            "comment": 40000,
            "series": "奇葩小国",
            "tags": ["奇葩小国", "历史", "刚果金", "非洲"],
        },
        {
            "bvid": "BV1b4411o002",
            "aid": 100003,
            "title": "CIA的秘密战争",
            "description": "CIA在全球的秘密行动",
            "duration": "28:00",
            "pubdate": 1625000000,
            "play": 6000000,
            "comment": 60000,
            "series": "神奇组织",
            "tags": ["神奇组织", "历史", "CIA", "间谍", "冷战"],
        },
        {
            "bvid": "BV1c4411o003",
            "aid": 100004,
            "title": "阿道夫·托卡契夫",
            "description": "苏联工程师的故事",
            "duration": "40:00",
            "pubdate": 1780025410,
            "play": 3000000,
            "comment": 30000,
            "series": "硬核狠人",
            "tags": ["硬核狠人", "历史", "苏联", "间谍", "冷战"],
        },
        {
            "bvid": "BV1d4411o004",
            "aid": 100005,
            "title": "索马里海盗兴衰史",
            "description": "索马里海盗的前世今生",
            "duration": "35:00",
            "pubdate": 1628000000,
            "play": 7000000,
            "comment": 70000,
            "series": "奇葩小国",
            "tags": ["奇葩小国", "历史", "索马里", "非洲"],
        },
    ],
}

MOCK_VIDEOS_WANGXIAO = {
    "uid": 52165725,
    "name": "王骁Albert",
    "fetched_at": "2026-06-03T12:00:00",
    "count": 4,
    "videos": [
        {
            "bvid": "BV1e4411o005",
            "aid": 200001,
            "title": "非洲新冷战：大国在非洲的博弈",
            "description": "中美俄在非洲的战略竞争",
            "duration": "15:00",
            "pubdate": 1750000000,
            "play": 500000,
            "comment": 5000,
            "series": "骁话一下",
            "tags": ["骁话一下", "国际关系", "非洲", "中国外交"],
        },
        {
            "bvid": "BV1f4411o006",
            "aid": 200002,
            "title": "刚果金的资源政治",
            "description": "刚果民主共和国的矿产资源与国际政治",
            "duration": "18:00",
            "pubdate": 1751000000,
            "play": 400000,
            "comment": 4000,
            "series": "骁话一下",
            "tags": ["骁话一下", "国际关系", "刚果金", "非洲", "资源"],
        },
        {
            "bvid": "BV1g4411o007",
            "aid": 200003,
            "title": "2026经济展望",
            "description": "全球宏观经济分析",
            "duration": "12:00",
            "pubdate": 1752000000,
            "play": 300000,
            "comment": 3000,
            "series": "",
            "tags": ["经济", "金融"],
        },
        {
            "bvid": "BV1h4411o008",
            "aid": 200004,
            "title": "小王在日本：文化观察",
            "description": "日本社会文化漫谈",
            "duration": "10:00",
            "pubdate": 1753000000,
            "play": 200000,
            "comment": 2000,
            "series": "",
            "tags": ["小王看世界", "日本", "文化"],
        },
    ],
}

MOCK_ANALYSIS_XIAOYUEHAN = [
    {
        "title": "阿尔巴尼亚：碉堡之国",
        "summary": "阿尔巴尼亚在霍查统治下建造了数十万个碉堡，成为世界上人均碉堡最多的国家。",
        "key_points": ["霍查时期修建了70万个碉堡", "阿尔巴尼亚与中苏关系", "碉堡至今仍是旅游景点"],
        "timeline": ["1944年霍查上台", "1961年与苏联决裂", "1978年与中国决裂"],
        "entities": {"countries": ["阿尔巴尼亚", "苏联", "中国"], "people": ["霍查"], "organizations": [], "events": ["中阿决裂"]},
        "topics": ["冷战", "碉堡", "社会主义"],
        "region": "欧洲",
        "category": "历史",
    },
    {
        "title": "刚果金的资源诅咒",
        "summary": "刚果民主共和国拥有丰富的矿产资源，却因资源诅咒陷入持续动荡。",
        "key_points": ["刚果金矿产丰富", "殖民历史影响深远", "资源冲突导致内战"],
        "timeline": ["1885年比利时殖民", "1960年独立", "1996-2003年刚果战争"],
        "entities": {"countries": ["刚果民主共和国", "比利时"], "people": ["蒙博托", "卡比拉"], "organizations": ["联合国"], "events": ["刚果战争"]},
        "topics": ["非洲", "资源诅咒", "殖民"],
        "region": "非洲",
        "category": "历史",
    },
    {
        "title": "CIA的秘密战争",
        "summary": "冷战期间CIA在全球进行的秘密行动，从推翻政权到暗杀计划。",
        "key_points": ["CIA的成立与扩张", "中情局在拉美的行动", "与克格勃的谍战"],
        "timeline": ["1947年CIA成立", "1953年伊朗政变", "1961年猪湾事件"],
        "entities": {"countries": ["美国", "伊朗", "古巴"], "people": [], "organizations": ["CIA", "KGB"], "events": ["伊朗政变", "猪湾事件"]},
        "topics": ["冷战", "间谍", "政变"],
        "region": "全球",
        "category": "军事",
    },
    {
        "title": "阿道夫·托卡契夫",
        "summary": "苏联工程师托卡契夫为CIA提供情报的传奇故事。",
        "key_points": ["托卡契夫主动联系CIA", "提供了苏联航空雷达核心机密", "最终被克格勃识破"],
        "timeline": [],
        "entities": {"countries": ["苏联", "美国"], "people": ["阿道夫·托卡契夫"], "organizations": ["CIA", "克格勃"], "events": []},
        "topics": ["冷战", "间谍"],
        "region": "欧洲",
        "category": "人物",
    },
    {
        "title": "索马里海盗兴衰史",
        "summary": "索马里海盗从渔民生计到国际安全威胁的演变过程。",
        "key_points": ["索马里内战后海盗兴起", "国际护航行动", "海盗产业的终结"],
        "timeline": ["1991年索马里内战", "2008年海盗危机高峰", "2012年后大幅减少"],
        "entities": {"countries": ["索马里"], "people": [], "organizations": ["欧盟反海盗部队"], "events": ["索马里内战"]},
        "topics": ["非洲", "海盗", "国际安全"],
        "region": "非洲",
        "category": "历史",
    },
]

MOCK_ANALYSIS_WANGXIAO = [
    {
        "title": "非洲新冷战：大国在非洲的博弈",
        "summary": "中美俄在非洲大陆的战略竞争，涉及基建投资、资源争夺和军事存在。",
        "key_points": ["中国在非洲的基建投资", "美国重返非洲战略", "俄罗斯瓦格纳在非洲"],
        "timeline": [],
        "entities": {"countries": ["中国", "美国", "俄罗斯", "尼日利亚", "肯尼亚"], "people": [], "organizations": ["一带一路", "瓦格纳"], "events": []},
        "topics": ["非洲", "国际关系", "地缘政治"],
        "region": "非洲",
        "category": "时政",
    },
    {
        "title": "刚果金的资源政治",
        "summary": "分析刚果金的钴矿和钶钽铁矿如何成为大国博弈的焦点。",
        "key_points": ["刚果金占全球钴产量的70%", "中国企业主导矿产开采", "西方国家的供应链焦虑"],
        "timeline": [],
        "entities": {"countries": ["刚果民主共和国", "中国", "美国"], "people": [], "organizations": ["洛阳钼业"], "events": []},
        "topics": ["非洲", "资源", "供应链"],
        "region": "非洲",
        "category": "时政",
    },
    {
        "title": "2026经济展望",
        "summary": "对2026年全球宏观经济的分析和预测。",
        "key_points": ["全球经济增速放缓", "通胀压力缓解", "新兴市场机遇"],
        "timeline": [],
        "entities": {"countries": ["中国", "美国"], "people": [], "organizations": ["IMF", "世界银行"], "events": []},
        "topics": ["经济", "宏观"],
        "region": "全球",
        "category": "经济",
    },
    {
        "title": "小王在日本：文化观察",
        "summary": "在日本生活的文化观察和思考。",
        "key_points": ["日本的职人精神", "东京的城市规划", "中日文化差异"],
        "timeline": [],
        "entities": {"countries": ["日本", "中国"], "people": [], "organizations": [], "events": []},
        "topics": ["日本", "文化"],
        "region": "亚洲",
        "category": "社会",
    },
]


def create_mock_data():
    raw_dir = os.path.join(PROJECT_DIR, "data", "raw")
    subs_dir = os.path.join(PROJECT_DIR, "data", "subtitles")
    os.makedirs(raw_dir, exist_ok=True)

    with open(os.path.join(raw_dir, "xiaoyuehan_videos.json"), "w", encoding="utf-8") as f:
        json.dump(MOCK_VIDEOS_XIAOYUEHAN, f, ensure_ascii=False, indent=2)
    with open(os.path.join(raw_dir, "wangxiao_videos.json"), "w", encoding="utf-8") as f:
        json.dump(MOCK_VIDEOS_WANGXIAO, f, ensure_ascii=False, indent=2)

    for up_name, vids, analyses in [
        ("小约翰可汗", MOCK_VIDEOS_XIAOYUEHAN["videos"], MOCK_ANALYSIS_XIAOYUEHAN),
        ("王骁Albert", MOCK_VIDEOS_WANGXIAO["videos"], MOCK_ANALYSIS_WANGXIAO),
    ]:
        sub_dir = os.path.join(subs_dir, up_name)
        os.makedirs(sub_dir, exist_ok=True)
        for v, analysis in zip(vids, analyses):
            txt_path = os.path.join(sub_dir, f"{v['bvid']}.txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(f"Mock subtitle for {v['title']}\n")
                f.write(f"这是一段模拟的字幕文本，用于测试笔记生成流程。\n" * 20)

    print("Mock data created successfully.")


def test_generate_notes():
    print("\n--- Testing generate_notes (full + skeleton mode) ---")

    for up_name, vids, analyses in [
        ("小约翰可汗", MOCK_VIDEOS_XIAOYUEHAN["videos"], MOCK_ANALYSIS_XIAOYUEHAN),
        ("王骁Albert", MOCK_VIDEOS_WANGXIAO["videos"], MOCK_ANALYSIS_WANGXIAO),
    ]:
        for v, analysis in zip(vids, analyses):
            series = generate_notes.classify_series(v, up_name)
            out_dir = os.path.join(PROJECT_DIR, series)
            os.makedirs(out_dir, exist_ok=True)
            out_path = os.path.join(out_dir, f"{v['bvid']}.md")

            # Alternate: full note vs skeleton
            idx = vids.index(v)
            if idx % 2 == 0:
                note = generate_notes.build_note(v, series, analysis)
                note_type = "full"
            else:
                note = generate_notes.build_skeleton_note(v, series)
                note_type = "skeleton"

            with open(out_path, "w", encoding="utf-8") as f:
                f.write(note)
            print(f"  [{note_type}] {series}/{v['bvid']}.md -> {analysis['title']}")

    print(f"  Done! Mixed full + skeleton notes created.")


def test_build_mocs():
    print("\n--- Testing build_mocs ---")
    build_mocs.main()


def main():
    create_mock_data()
    test_generate_notes()
    test_build_mocs()
    print("\n=== All tests passed! ===")
    print("\nGenerated directories:")
    for d in sorted(os.listdir(PROJECT_DIR)):
        dpath = os.path.join(PROJECT_DIR, d)
        if os.path.isdir(dpath) and d.startswith("0"):
            count = len([f for f in os.listdir(dpath) if f.endswith(".md")])
            print(f"  {d}/ ({count} files)")


if __name__ == "__main__":
    main()
