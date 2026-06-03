# 王骁 × 小约翰可汗 Obsidian 知识库 | Wang Xiao × Xiaoyuehan Knowledge Base

整理自 B 站 UP 主 **[王骁Albert](https://space.bilibili.com/52165725)** 和 **[小约翰可汗](https://space.bilibili.com/23947287)** 的视频系列，用 Obsidian 笔记重新组织，方便检索和关联。

> **English** — An Obsidian vault organizing content from two popular Chinese Bilibili creators: **Wang Xiao Albert** (political commentary, international relations) and **Xiaoyuehankehan** (world history). Covers geopolitics, bizarre small nations, weird organizations, and hardcore legends. AI-powered note generation with YAML metadata, MOC indexes, and bidirectional links. Read the [English section](#english) below.

## 里面有什么

| 目录 | UP 主 | 系列 | 说明 |
|------|-------|------|------|
| `01-奇葩小国` | 小约翰可汗 | 奇葩小国 | 亚非拉第三世界小国历史 |
| `02-神奇组织` | 小约翰可汗 | 神奇组织 | 国际奇特组织 |
| `03-硬核狠人` | 小约翰可汗 | 硬核狠人 | 传奇人物 |
| `04-骁话一下` | 王骁Albert | 骁话一下 | 国际时政深度分析 |
| `05-王骁其他` | 王骁Albert | 主频道其他 | 理财、社会话题等 |
| `06-小王看世界` | 王骁Albert | 副频道 | 文化、生活观察 |
| `00-主题索引` | — | 跨 UP 主 MOC | 按地区、国家、主题聚合的索引页 |

另外还有 `首页.md`（总导航）、`小约翰可汗.md` 和 `王骁Albert.md`（作者介绍）。

## 有什么特点

**跨 UP 主联动**。两个 UP 主都涉及非洲、国际关系、资源政治等话题。主题索引把相关内容聚合在一起——比如「非洲」主题下既有王骁的时政分析，也有小约翰的历史故事。

**YAML 元数据完整**。每篇笔记都有 frontmatter，标明了系列、期数、BV 号、国家、地区、相关主题等字段，方便 Obsidian Dataview 查询：

```yaml
---
title: "非洲新冷战：大国在非洲的博弈"
created: 2026-06-03T10:00:00
category: 时政
source: "[[王骁Albert]]"
series: "骁话一下"
bv: BV1e4411o005
country: 刚果民主共和国
region: 非洲
topic:
  - 国际关系
  - 地缘政治
  - 非洲
related:
  - 刚果民主共和国
  - 中国
  - 美国
  - 国际关系
  - 非洲
---
```

**主题索引（MOC）**。`00-主题索引/` 下按地区、国家、主题三个维度聚合笔记，把散落在不同 UP 主、不同系列里的相关篇章聚合到一起。

**AI 辅助生成**。使用 DeepSeek V4 从视频字幕自动提炼结构化笔记——摘要、关键信息、时间线、相关实体。由 `scripts/` 下的 Python 工具链批量处理。

**双向链接**。笔记之间用 `[[wikilink]]` 互相关联——人名、组织名、国家名、主题都能跳转。

## 怎么用

1. 安装 [Obsidian](https://obsidian.md)
2. 克隆仓库到本地

```bash
git clone https://github.com/yyz197/wang-xiao-knowledge.git
```

3. 打开 Obsidian → 打开文件夹 → 选 `wang-xiao-knowledge`
4. 完事

推荐插件：

- **Dataview** — 用 YAML 元数据做筛选和统计
- **Graph View** — 自带的，打开看看两个 UP 主内容的关联网络

## 脚本工具

`scripts/` 下是笔记生成的完整流水线：

```bash
# 1. 安装依赖
pip install -r scripts/requirements.txt

# 2. 配置 DeepSeek API Key
cp .env.example .env
# 编辑 .env 填入你的 DEEPSEEK_API_KEY

# 3. 拉取视频列表（需从非风控 IP 运行）
python scripts/fetch_videos.py

# 4. 下载字幕
python scripts/fetch_subtitles.py

# 5. AI 生成笔记
python scripts/generate_notes.py

# 6. 构建主题索引
python scripts/build_mocs.py
```

### 注意事项

- **IP 风控**：`fetch_videos.py` 需要从未被 B 站风控的 IP 运行。如遇 `-352` 或 `-412` 错误，请设置代理：`export HTTP_PROXY=http://127.0.0.1:7890`
- **字幕覆盖率**：并非所有视频都有字幕。`fetch_subtitles.py` 会自动跳过无字幕视频
- **API 费用**：`generate_notes.py` 调用 DeepSeek API，每篇笔记约消耗 1000-4000 tokens

## 内容说明

- 笔记内容整理自公开视频，仅供个人学习和参考
- 每篇笔记都标注了原视频 BV 号
- AI 生成内容可能存在偏差，建议以原视频为准
- 如有内容错误欢迎提 Issue 或 PR

## License

CC BY-NC-SA 4.0 — 可自由分享和改编，请注明来源，不得商用。

---

## English

An Obsidian knowledge base combining content from two leading Chinese Bilibili creators:

- **[Wang Xiao Albert](https://space.bilibili.com/52165725)** — former Guancha.cn editor, covers geopolitics and global affairs (250K+ subscribers)
- **[Xiaoyuehankehan](https://space.bilibili.com/23947287)** — history storyteller known for uncovering overlooked corners of world history (10M+ subscribers)

Their content intersects on topics like Africa, Cold War history, resource politics, and international relations — this vault makes those connections visible.

### Features

- **Cross-creator linking** — shared topic indexes connect Wang Xiao's current affairs analysis with Xiaoyuehan's historical narratives
- **YAML frontmatter** — every note includes source, series, country, region, and topics, ready for Dataview queries
- **AI-powered generation** — DeepSeek V4 converts video subtitles into structured notes with summaries, key points, and timelines
- **MOC topic indexes** — auto-generated index pages by region, country, and topic
- **Bidirectional wikilinks** — people, organizations, countries, and events link across notes

### Quick start

```bash
git clone https://github.com/yyz197/wang-xiao-knowledge.git
```

Open the folder as an Obsidian vault. Recommended plugins: **Dataview** for metadata queries.

### Script pipeline

See [scripts/](scripts/) for the full data pipeline:

1. `fetch_videos.py` — fetch video list from Bilibili API (WBI signed)
2. `fetch_subtitles.py` — download and clean subtitles
3. `generate_notes.py` — generate structured notes via DeepSeek V4
4. `build_mocs.py` — build topic index pages

### Content disclaimer

All content is derived from publicly available videos, intended for personal study only. Each note includes the original Bilibili BV ID for reference. AI-generated content may contain inaccuracies — please refer to original videos for authoritative information. Corrections welcome via Issues or PRs.
