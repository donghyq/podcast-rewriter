# Podcast Rewriter

> 长篇调研文档 → 播客风格深度改写工具

将上百页的调研文档（docx/md/txt）按指定播客博主的语言风格，深度改写为口语化播客脚本，并自动生成格式化 Word 文档。最初为法律合规调研文档设计，适用于任何长文档的"能听化"改写。

## 核心特性

- **风格复刻** — 分析目标博主的语气词、句式、叙事结构，生成 style profile，改写内容自带该风格
- **多 Agent 并行深度改写** — 原文按主题拆分为子章节，每个子章节由独立 agent 深度改写（支持联网检索补充数据和案例）
- **深度规范约束** — 压缩比红线（原文每 1 万字 ≥ 3000 字输出）、专家观点完整保留、四层解读框架，杜绝"摘要式"改写丢知识点
- **Word 自动生成** — 正文宋体 11 号、3 倍行距、蓝色标题，分章节输出 + 全文汇总

## 工作流程

```
原始文档 (docx)
    │
    ▼
[extract_source.py]  按章节拆分原文 → source/*.txt
    │
    ▼
风格分析（博主文字稿样本）→ style_profile.md
    │
    ▼
子章节拆分（每节 5000-10000 字原文）
    │
    ▼
多 Agent 并行深度改写（每个子章节一个 agent）
    │
    ▼
[combine.py]  合并子章节 → 各章节 Word + 全文汇总 Word
```

## 安装

```bash
git clone https://github.com/donghyq/podcast-rewriter.git
pip install python-docx
```

可选（需要 TTS 音频时）：

```bash
pip install edge-tts pydub
```

## 使用

### 1. 提取原文

```bash
python scripts/extract_source.py 素材.docx --output-dir source/
```

按 Heading 1 边界拆分为章节 txt 文件，每段带 `[NNN]` 索引前缀，方便 agent 定位段落范围。

### 2. 生成风格指南

复制 `templates/style_profile_template.md`，填入目标博主的风格分析（语气词、句式、叙事结构、受众定位、深度要求）。

**深度改写规范**（模板已内置，可按需调整）：

| 规范 | 说明 |
|------|------|
| 压缩比红线 | 原文每 1 万字，输出不少于 3000 字 |
| 专家观点 | 姓名+机构+论点+论据完整呈现，不能"有学者认为"一笔带过 |
| 四层解读 | 背景意义 → 适用对象 → 规则细节 → 实务场景 |
| 数据支撑 | 提到"影响/依赖"必须给数据和企业案例 |
| 拆分粒度 | 一个子章节一个主题，目标 5000-8000 字 |

### 3. Agent 改写

为每个子章节启动一个 LLM agent（提示词模板见 `SKILL.md`），核心要求：

- 严格遵循 style_profile.md
- 深度展开而非压缩概括
- 原文缺数据时联网检索补充

> 本项目设计为在 [WorkBuddy](https://www.codebuddy.cn/docs/workbuddy/Overview) / CodeBuddy 等 Agent 环境中运行，agent 编排由宿主完成。任何支持并行调用 LLM 的框架均可套用此流程。

### 4. 合并生成 Word

编写章节配置 JSON（参考 `templates/chapters.example.json`）：

```json
{
    "02_第一章": [
        "script/v4/ch1_01.md",
        "script/v4/ch1_02.md",
        "script/v4/ch1_03.md"
    ]
}
```

```bash
python scripts/combine.py --base-dir output/ --config chapters.json
```

输出各章节 Word + `全文_播客脚本.docx`。

### 单文件转换

```bash
python scripts/md_to_word.py input.md output.docx
```

## Word 格式

- 正文：宋体 11pt，3 倍行距，首行缩进 22pt
- 标题：蓝色 RGB(31, 73, 125)
- 页边距：上下 1 英寸，左右 1.25 英寸

## 实战效果

20 万字法律合规调研文档（中美欧数据监管方向）：

| 指标 | 普通摘要式改写 | 本工具深度改写 |
|------|--------------|--------------|
| 输出字数 | ~5.6 万字（压缩比 3.6:1，大量知识点丢失） | ~20 万字（1:1 深度展开） |
| 学者观点 | "有学者认为"式引用 | 姓名+机构+完整论证逻辑 |
| 监管工具 | 念条文 | 立法背景/受影响企业/中外企业影响/关联法规 |
| 数据案例 | 抽象词汇 | 具体数据+企业名单+行业案例 |

## 作为 WorkBuddy Skill 使用

本仓库同时是一个 WorkBuddy Skill。将仓库克隆到 `~/.workbuddy/skills/podcast-rewriter/`，在对话中说"按播客风格改写"即可自动触发。

## License

MIT
