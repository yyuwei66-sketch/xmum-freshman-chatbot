# Source Material

Text Preprocessing + Rule-Based Intent Detection

Create a professional PowerPoint section for my part: "Combined NLP Layer: Text Preprocessing + Rule-Based Intent Detection".

Context:
This is for an AIT103 Introduction to Intelligence Application group project: "A Hybrid and ML-Enhanced FAQ Chatbot for XMUM Freshman Enquiries". The chatbot uses a hybrid structure: rule-based handling, ML category classification, and retrieval-based answer matching. Retrieval-based chatbots commonly involve intent classification and response selection.

Make 4 slides:

Slide 1 - Section Title
Title: Combined NLP Layer
Subtitle: Text Preprocessing + Rule-Based Intent Detection
Purpose: Standardize user input and quickly route it before FAQ classification/retrieval.
Visual: pipeline-style graphic: User Input -> Preprocessing -> Intent Detection -> FAQ Route / Direct Reply.
Bottom-right footer on every slide:
CHEN MOAHN
AIT2509003

Slide 2 - Text Preprocessing
Explain four steps:
1. Text normalization: lowercase, remove extra punctuation and spaces.
2. Tokenization: split sentence into words.
3. Stopword removal: remove low-information words such as "the", "is", "please".
4. Conservative stemming: unify simple word forms such as plurals or verb changes.
Mention: implemented as a lightweight hand-written prototype, without third-party NLP libraries, so rules can be customized for XMUM scenarios.
Visual: before/after example:
"Where's the Wi-Fi office, please???" -> "where wifi office"
During tokenization, expand "where's" into the two tokens "where" and "is".

Slide 3 - Rule-Based Intent Detection
Explain:
This layer quickly detects inputs that do not need FAQ retrieval:
hi / thanks / bye / who are you / help
For these, the chatbot directly returns fixed responses.
Then add FAQ template detection:
"where is..." -> location
"how can I..." -> procedure
"who should I contact..." -> contact
"when is the deadline..." -> deadline
Visual: decision tree:
User query -> Small talk? yes -> fixed reply
no -> FAQ template? yes -> route to category
no -> ML classifier + retrieval

Slide 4 - Why This Layer Matters
Key points:
- Acts as the first filter and router of the chatbot.
- Reduces noise before ML classification.
- Makes different spellings more consistent, e.g. Wi-Fi / wifi / wi fi.
- Improves stability of category classification and answer retrieval.
- Keeps the chatbot lightweight, explainable, and suitable for a campus FAQ system.
End with one sentence:
"Although this module is simple, it is the foundation that makes the whole FAQ chatbot more stable and controllable."

Design requirements:
Use a clean university-style design with XMUM blue, white, and light grey.
Use large readable fonts, minimal text, and clear icons.
Avoid crowded paragraphs.
Use diagrams and flow arrows more than text boxes.
Keep the style consistent with an academic presentation.
Add the footer "CHEN MOAHN / AIT2509003" at the bottom-right corner of every slide.
