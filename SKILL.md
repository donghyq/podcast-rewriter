---
name: podcast-rewriter
description: 将长篇调研文档按指定播客风格改写为播客脚本+Word，支持多agent并行深度改写
version: 1.0.0
agent_created: true
triggers:
  - "播客改写"
  - "按播客风格改写"
  - "podcast rewrite"
  - "改写为播客脚本"
  - "播客脚本生成"
---

# Podcast Rewriter — 播客风格深度改写工具

## 用途

将长篇调研文档（docx/md/txt）按指定播客博主风格，深度改写为播客对话体脚本，并生成格式化Word文档。

适用场景：
- 法律/合规/政策调研文档 → 播客脚本
- 企业内训材料 → 播客形式
- 学术论文/研究报告 → 口语化解读
- 任何长文档需要"变成能听的内容"

## 工作流程

### 第1步：提取原文

读取原始docx文件，按章节拆分为txt源文件。

```python
# 使用 python-docx 读取
from docx import Document
doc = Document("原始素材.docx")
# 按标题层级拆分章节
```

### 第2步：风格分析

如果用户提供了播客博主的文字稿/截图，分析其风格特征，生成 `style_profile.md`。

分析维度：
- **语言质感**：语气词、句子长度、口语化程度
- **叙事结构**：先倒带再开场、先总纲再拆细节、类比先行
- **逻辑方式**：用已知解释未知、先定义再分析、正反并举
- **语气基调**：旁观者视角、好奇感、适度调侃

将风格特征固化为 style_profile.md，作为改写agent的system prompt。

**参考模板**：`templates/style_profile_template.md`

### 第3步：拆分子章节

将原文按主题拆分为多个子章节（每节5000-10000字原文），写入 `source/` 目录。

拆分原则：
- 按原文的标题层级自然拆分
- 过长的章节（>2万字）需进一步细分
- 每个子章节聚焦一个主题

### 第4步：多agent并行深度改写

为每个子章节启动一个独立agent（使用 Agent 工具，`run_in_background: true`）。

**agent prompt 模板**：

```
你是一位面向[受众定位]的播客脚本写手。

## 任务
深度改写播客脚本"[章节名称]"。

## 源文件
读取文件 `[source/chXX_YY.txt]`，聚焦段落 [起始] 到 [结束]。

## 风格指南
读取文件 `style_profile.md`，严格遵循其中的所有规范。

## 深度要求
1. 学者/专家观点必须完整保留并展开——谁说的、说了什么、为什么这么说
2. [其他深度要求，根据文档主题调整]

## 网络检索
通过WebSearch搜索补充：[需要补充的数据/案例]

## 输出
写到文件 `script/v4/chXX_YY.md`

字数要求：[5000-10000]字。宁可详细，不可遗漏。
```

**并行启动**：所有agent在一条消息中同时启动（多个Agent工具调用）。

### 第5步：合并与生成Word

所有子章节完成后，运行合并脚本：

```bash
python scripts/combine.py --base-dir output/ --chapters-config chapters.json
```

或手动合并：
```bash
python scripts/md_to_word.py input.md output.docx
```

## 关键规范

### 深度改写红线（必须遵守）

1. **压缩比**：原文每1万字，输出不少于3000字
2. **学者观点**：必须完整保留——姓名+机构+论点+论据
3. **地缘政治/行业分析**：结合时代背景、历史脉络、深层逻辑，不能三言两语
4. **监管工具/法规**：四层解读——立法背景→适用对象→规则细节→实务场景
5. **数据支撑**：提到"影响""依赖"时必须给数据和案例
6. **中外企业影响**：每部法规分析对中国企业和外国企业分别的影响

### Word格式

- 正文：宋体 11pt，3倍行距，首行缩进22pt
- 标题：蓝色 RGB(31,73,125)
- 页边距：上下1英寸，左右1.25英寸

## 文件结构

```
output/
├── source/              # 原文拆分后的txt文件
│   ├── ch1_xxx.txt
│   └── ch2_xxx.txt
├── style_profile.md     # 风格指南（核心文件）
├── script/
│   └── v4/              # 改写后的Markdown
│       ├── ch1_01_xxx.md
│       └── ...
├── word_v4/             # 最终Word文件
│   ├── 01_xxx.docx
│   └── 全文_xxx.docx
└── combine.py           # 合并脚本
```

## 依赖

```bash
pip install python-docx
# TTS（可选）：pip install edge-tts pydub
```

## 注意事项

- **受众定位**：在style_profile.md中明确定义（法律人/行业从业者/普罗大众），影响改写深度
- **知识补充**：原文简单带过的知识点要展开，但要自然嵌入叙述
- **口语化≠浅薄**：语言风格口语化，但内容要有专业深度
- **agent数量**：根据原文长度决定，一般每个子章节一个agent，总共10-20个并行
- **网络检索**：agent应使用WebSearch补充原文缺少的数据和案例
