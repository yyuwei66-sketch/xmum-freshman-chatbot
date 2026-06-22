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
- 每个节点下方两行字：英文节点名 + 一句极短说明（爬取 / 预处理 / 切块 / 分类 / 生成FAQ / 数据增强 / 校验 / 入库

**第3页 预处理**

- 页面标题：Highlight 1 — Cleaning the Raw Text
- 左侧Before区块标题"Before"：乱线条模拟噪音文本，下方标签：Emojis / Broken line breaks / Incomplete sentences
- 右侧After区块标题"After"：整齐的H1/H2/H3标题层级结构示意
- 底部三个关键词标签：Noise Removal / Manual Review per Article / 206 Chunks

**第4页 切块标注规则（独立一页）**

- 页面标题：Highlight 1 — Split by Heading Level
- 顶部说明行：Default: each H2 and H3 generates one independent chunk
- 4张卡片并排，每张有标记符号、位置、效果三行文字：
    - 卡片1：`@` after `###` → H3 merges into parent H2
    - 卡片2：`@` after `##` → Entire H2 becomes one chunk
    - 卡片3：`@` after `#` → All H3s ignored, split by H2 only
    - 卡片4：`%` after `#` → Normal split + one extra H1-level chunk
- 每张卡片配合并/分裂小图标
- 底部标签行：Output levels: `h2` / `h3` / `h1_full`

**第5页 分类（数据图表页，做得最visual）**

- 页面标题：Highlight 2 — 8 Categories by Keyword Matching
- 环形图展示8个分类chunk占比：campus_life 81 / accommodation_living 28 / academic_affairs 23 / transportation 23 / registration_orientation 18 / campus_services 13 / it_support 10 / finance_fees 9
- 每个扇形配不同强调色，图例配英文类别名
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

**第8页 成果数据（仪表盘风格）**

- 页面标题：Results 
- 顶部5个仪表盘数字卡片（各有标签）：206 Chunks / 492 FAQs / 8 Categories / 0 Errors / ~20 min
- 柱状图标题"FAQs by Category"，展示8个分类数量：Academic Affairs 56 / IT Support 23 / Registration 42 / Campus Services 26 / Accommodation 70 / Transportation 53 / Finance 25 / Campus Life 197
- 右下角两行：Handbook pipeline: 615 FAQs / Total knowledge base: 1,107 entries（2,400+ phrasings after augmentation）