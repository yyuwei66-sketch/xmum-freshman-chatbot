# Video Outline

> **主题**：`warm-keynote` - 奶油纸底、青色强调、暖色网格，适合清晰的 SaaS / academic keynote.
> **总时长**：约 1 分 18 秒（英文口播约 300 words）
> **章节数**：4 章 / 16 步

---

## 1. combined-layer - Combined NLP Layer（2 steps · ~9s）

**信息池**：
- 项目：AIT103 Introduction to Intelligence Application group project —— 来源 article L4-L5
- 系统主题："A Hybrid and ML-Enhanced FAQ Chatbot for XMUM Freshman Enquiries" —— 来源 article L5
- 混合结构：rule-based handling, ML category classification, retrieval-based answer matching —— 来源 article L5
- 模块目的：standardize user input and quickly route it before FAQ classification/retrieval —— 来源 article L10-L13

**开发计划**：

- step 1 (~4s) - Hero title: messy input becomes a controlled NLP route.
- step 2 (~5s) - Pipeline: User Input -> Preprocessing -> Intent Detection -> Direct Reply / FAQ Route.

口播节选：
> User input is messy. The Combined NLP Layer cleans it first, then routes it fast.

---

## 2. preprocessing - Text Preprocessing（6 steps · ~31s）

**信息池**：
- Four steps：normalization, tokenization, stopword removal, conservative stemming —— 来源 article L18-L24
- Before/after example："Where's the Wi-Fi office, please???" -> "where wifi office"；tokenization expands "where's" into "where" + "is" —— 来源 article L25-L26
- Implementation：lightweight hand-written prototype, without third-party NLP libraries —— 来源 article L24
- Customization：rules can be customized for XMUM scenarios —— 来源 article L24

**开发计划**：

- step 1 (~5s) - Begin one continuous example path by normalizing "Where's the Wi-Fi office, please???".
- step 2 (~5s) - Continue the same path; tokenization expands "where's" into "where" + "is" and splits all words.
- step 3 (~5s) - Continue the same path; stopword removal dims "is", "the", and "please".
- step 4 (~6s) - Continue the same path; conservative stemming keeps the remaining base forms unchanged.
- step 5 (~5s) - Before/after example turns into "where wifi office".
- step 6 (~5s) - Lightweight prototype note: hand-written, customizable for XMUM.

口播节选：
> So "Where's the Wi-Fi office, please???" becomes "where wifi office".

---

## 3. rule-intent - Rule-Based Intent Detection（4 steps · ~24s）

**信息池**：
- Direct responses：hi / thanks / bye / who are you / help —— 来源 article L28-L32
- FAQ templates：where is -> location; how can I -> procedure; who should I contact -> contact; when is the deadline -> deadline —— 来源 article L33-L37
- Decision tree：Small talk -> fixed reply; FAQ template -> route to category; otherwise ML classifier + retrieval —— 来源 article L38-L41

**开发计划**：

- step 1 (~4s) - Intent detection checks easy cases first.
- step 2 (~7s) - Small talk set routes to fixed replies.
- step 3 (~8s) - FAQ templates map query openings to categories.
- step 4 (~5s) - Non-matches continue to ML classifier + retrieval.

口播节选：
> If none of those rules match, the query continues to the ML classifier and retrieval-based answer matching.

---

## 4. why-matters - Why This Layer Matters（4 steps · ~16s）

**信息池**：
- First filter and router —— 来源 article L43-L45
- Reduces noise before ML classification —— 来源 article L46
- Normalizes spelling variants：Wi-Fi / wifi / wi fi —— 来源 article L47
- Improves stability of category classification and answer retrieval —— 来源 article L48
- Lightweight, explainable, suitable for campus FAQ —— 来源 article L49
- Closing sentence：foundation that makes the whole FAQ chatbot more stable and controllable —— 来源 article L50-L51

**开发计划**：

- step 1 (~4s) - First filter/router sits at the front of the system.
- step 2 (~5s) - Noise reduction and spelling consistency are shown as two impact lanes.
- step 3 (~3s) - Stability flows into category classification and retrieval.
- step 4 (~4s) - Closing quote: simple foundation, stable and controllable chatbot.

口播节选：
> Although this module is simple, it is the foundation that makes the whole FAQ chatbot more stable and controllable.

---

## 素材清单

### 1. combined-layer
- ✓ Pipeline diagram drawn in CSS/SVG.

### 2. preprocessing
- ✓ Before/after example drawn in CSS.
- ✓ Word chips and cleaning rail drawn in CSS.

### 3. rule-intent
- ✓ Decision tree drawn in CSS/SVG.
- ✓ Intent/template chips drawn in CSS.

### 4. why-matters
- ✓ Impact lanes and stability flow drawn in CSS/SVG.

## 自检

- [x] 每个 step 都是单一句屏幕内容描述，没有写具体动画实现。
- [x] 每章信息池至少 3 条，并标注来源。
- [x] step 估时累加约等于顶部总时长。
- [x] 章节切分为 3-6 步，适合课堂展示。
- [x] 素材清单按章节列出，全部为可绘制视觉素材。
