请帮我生成一个可在浏览器直接打开的演讲用HTML幻灯片（单文件，内嵌CSS+JS，支持左右键盘/点击箭头翻页）大量留白，字不要大段大段的，核心靠图表和关键词句传达信息，只放关键词、数字、流程节点。全部都用英文 

共8页，每页内容如下：

**第1页 封面**

- 标题：From Scattered Articles to Structured Knowledge
- 副标题：FAQ Data Pipeline for Freshmen Chatbot
- 视觉：两个零散文档图标（WeChat / Handbook）飘散汇聚成一个数据库图标

**第2页 Pipeline总览（最重要页，做得最好看）**

- 页面标题：The 8-Step Pipeline
- 横向流程图，8个节点依次排列：Crawl → Preprocess → Chunk → Classify → Generate FAQ → Augment → Validate → Export JSON
- 每个节点一个简洁图标，节点间箭头连接，节点依次高亮动画
- 每个节点下方两行字：英文节点名 + 一句极短说明：
- **Crawler** — fetch raw content
- **Preprocessor** — clean & format data
- **Chunker** — split documents
- **Classifier** — label data
- **FAQ_Generator** — build QA pairs
- **Augmenter** — enrich dataset
- **Validator** — ensure data quality
- **Ingestor** — write to storage

**第3页 Preprocessing**

- 页面标题：Highlight 1 — Cleaning the Raw Text
- 副标题小字：Raw WeChat articles contain noise that breaks machine parsing
- 左右对比布局，中间一个箭头分隔：
    - 左侧"Before"区块：用乱线条、随机符号模拟噪音文本，区块内散落标签：🎉 Emojis / ↵↵ Broken line breaks / … Incomplete sentences / 📷 Embedded images
    - 右侧"After"区块：整齐的层级结构示意，显示 # Title / ## Section / ### Subsection 三层缩进，区块内标签：Clean structure / Markdown-ready
- 底部三个关键词pill标签：✓ Auto Noise Removal　✓ Manual Review per Article　✓ 206 Chunks Output

**第4页 Chunking Rules**

- 页面标题：Highlight 1 — Split by Heading Level
- 副标题小字：Not by word count — by semantic heading structure
- 顶部说明条：Default: each `##` → 1 chunk / each `###` → 1 independent chunk
- 页面中央做一个切分动画（循环播放）：
    - 初始状态：一整块文档矩形，内部显示完整的层级结构加正文内容：

```
# Student Handbook
  ## Tuition & Fees
  All students must complete payment before the semester starts.
  ### Payment Methods
  You may pay via online banking or campus cashier.
  ### Deadlines
  Late payment incurs a penalty fee of RM50.
  ## Campus Services
  The university provides various support services for students.
  ### Library Access
  Students can borrow up to 5 books at a time.
```

- 动画过程：从每个标题行处出现荧光色横向切割线，像刀切一样依次切开，切开后各块带标签分离飘出并附上对应 level 标签：
    - `## Section A` + 正文 → **h2 chunk**（橙色边框）
    - `### Sub 1` + 正文 → **h3 chunk**（蓝色边框）
    - `### Sub 2` + 正文 → **h3 chunk**（蓝色边框）
    - `## Section B` + 正文 → **h2 chunk**（橙色边框）
    - `### Sub 3` + 正文 → **h3 chunk**（蓝色边框）
- 切割线用荧光绿，chunk块飘出后短暂停留再淡出，然后循环回初始状态
- 右侧4张小卡片竖排（补充说明）：
    - `@` after `###` → merges into H2
    - `@` after `##` → entire H2 = 1 chunk
    - `@` after `#` → H3s ignored
    - `%` after `#` → extra H1 chunk
- 底部标签行：Output levels: `h2` | `h3` | `h1_full`

**第5页 分类（数据图表页，做得最visual）**

- 页面标题：Highlight 2 — 8 Categories by Keyword Matching
- 环形图展示8个分类chunk占比：campus_life 81 / accommodation_living 28 / academic_affairs 23 / transportation 23 / registration_orientation 18 / campus_services 13 / it_support 10 / finance_fees 9
- 每个扇形配不同强调色，扇形图内每部分标占比，图例配英文类别名
- 图表旁三行突出文字：206 Chunks total / 8 Categories / 1 unmatched → resolved manually

**第6页 FAQ生成——三阶段渐进测试**

- - 页面标题：Highlight 3 — Progressive 3-Stage Testing
- 三个递进节点，每个节点有标题+3条子说明：
    - Stage 1 — Micro Test（2 chunks）：No fabrication / Correct format / H2 vs H3 depth
    - Stage 2 — Single Category Full Run：Concurrency delay / Timeout retry / Markdown cleanup
    - Stage 3 — All 8 Categories：Zero errors / Full production
- 节点间用递进箭头，底部小字：Progressive, not all-at-once

**第7页 数据增强**

- 页面标题：Highlight 4 —— Data Augmentation
- 左侧对比卡片（各有标题+说明）：
    - H2 Overview Level：Broad answer / 2–4 FAQs per chunk
    - H3 Detail Level：Focused answer / 2–3 FAQs per chunk
- 右侧气泡图：中间一个问题气泡，放射出5个不同样式小气泡
- 右侧底部：1 Question → 5 Phrasings → Better Retrieval Coverage

**第8页 Results**

- 页面标题：Results
- 顶部5个仪表盘数字卡片：206 Chunks / 492 FAQs / 8 Categories / 0 Errors / ~20 min
- 柱状图标题"FAQs by Category"，展示8个分类数量：Academic Affairs 56 / IT Support 23 / Registration 42 / Campus Services 26 / Accommodation 70 / Transportation 53 / Finance 25 / Campus Life 197
- 右下角数据来源对比：
    - WeChat Pipeline: 492 FAQs
    - Handbook Pipeline: 123 FAQs
    - Total: 615 entries（2,400+ phrasings after augmentation）