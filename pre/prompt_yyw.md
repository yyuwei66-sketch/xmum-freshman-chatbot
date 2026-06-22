Please revise my existing 3-slide HTML presentation for the project:

Nova: A Hybrid and ML-Enhanced FAQ Chatbot for XMUM Freshman Enquiries

Main goal:
Make the slides more readable, visually cohesive, and suitable for a classroom presentation. The current version has small text, too much empty space, and some fragmented layout. Keep the clean white-wall technical style, but make it more polished and impactful.

Important:
The frontend is HTML UI, not Streamlit. Replace all “Streamlit UI” with “HTML UI” or “Nova HTML UI”.

Global style:
- White / off-white background with subtle light-blue grid lines
- Modern technical presentation style
- Main colors: dark navy, bright blue, soft purple, and green for output/evaluation
- Larger fonts for projector readability
- Strong visual hierarchy
- Rounded cards, soft shadows, clean arrows
- Smooth HTML animations: fade-in, slight upward motion, moving dots on arrows, subtle glow on key modules
- Avoid tiny labels, excessive whitespace, and fragmented blocks
- Keep everything in a single HTML file with embedded CSS and JavaScript
- Keyboard navigation: Right/Space = next slide, Left = previous slide, F = fullscreen

Slide 1: Project Introduction
Title:
Nova
A Hybrid and ML-Enhanced FAQ Chatbot

Subtitle:
For XMUM Freshman Enquiries

Content:
A text-based HTML chatbot that retrieves reliable campus information from a structured FAQ knowledge base.

Visual:
Left side:
- Large “Nova”
- Subtitle and short description
- Keywords: Structured FAQ Knowledge Base · Rule-based Handling · ML Classification · Retrieval-based Answering · HTML UI

Right side:
- Central Nova chatbot node
- Connected module cards:
  1. FAQ Knowledge Base
  2. Rule-based Handling
  3. ML Classification
  4. Retrieval Matching
  5. Nova HTML UI
- Add animated dotted connection lines and moving data-flow dots
- Reduce empty space between left text and right diagram

Slide 2: Problem Formulation
Title:
Freshman Enquiries as an NLP + Retrieval Problem

Subtitle:
The system must understand informal student questions and retrieve reliable university answers.

Use three large readable cards:

1. Scattered Information
- Official emails
- Student handbook
- University platforms
- Orientation materials
- Peer group discussions

2. Unstructured Questions
- Same meaning, different wording
- Short and informal input
- Different student expressions
- Example: “Moodle login problem” vs “cannot access learning platform”

3. Reliable Answers
- Policy-related
- Procedure-related
- Need verified sources
- Avoid unsupported free-form generation

Bottom formula box:
Technical Formulation = Natural Language Understanding + Information Retrieval

Improve this slide:
- Increase card size and text size
- Reduce empty space inside cards
- Add subtle connector lines from the three cards to the formula box
- Make the formula box more visually prominent with a subtle blue glow or animated border

Slide 3: Overall System Structure
Replace the current third slide completely with the previous overall structure diagram, but redesign it for readability and cohesion.

Title:
Overall Structure of Nova

Subtitle:
Hybrid + ML-Enhanced FAQ Chatbot Architecture

Structure:
Three major zones:
1. Data Preparation
2. Runtime Pipeline
3. Evaluation

Left zone: Data Preparation
- Data Sources:
  official emails, student handbook, university platforms, peer group chats, orientation materials
- Data Standardization:
  clean, normalize, deduplicate, JSONL format
- FAQ Knowledge Base:
  faq_dataset.jsonl
  category, sub_category, question, answer, keywords, intent, contributor, verified

Center zone: Runtime Pipeline
- User Input (HTML UI)
- Text Preprocessing:
  normalization, tokenization, stopword removal
- Simple Intent Check:
  greeting, thanks, help, identity
- If simple intent:
  Rule-based Response → Chatbot Output
- If FAQ-related query:
  ML-Enhanced FAQ Retrieval

Inside ML-Enhanced FAQ Retrieval:
1. Category Classification
   TF-IDF features + Logistic Regression → predicted category
2. Category-specific Retrieval
   Search only within the predicted category
3. Similarity Ranking
   TF-IDF + Cosine Similarity → Top-K candidates
4. Confidence Assessment
   Similarity score + confidence thresholds
5. Response Strategy
   High confidence → direct answer
   Medium confidence → top 3 related questions
   Low confidence → fallback / clarification

Bottom output:
Chatbot Output (HTML UI)
- FAQ answer
- Predicted category
- Confidence score
- Top 3 related questions
- Recent chats / session history

Right zone: Evaluation
- Classification Accuracy: Precision / Recall / F1
- Model Comparison: baseline vs proposed
- Retrieval Quality: Precision@K / Recall@K / MRR
- User Experience: usability testing / user feedback

Slide 3 design requirements:
- Make Runtime Pipeline the visual center
- Use larger readable text
- Use blue for Data Preparation, purple for Runtime, green for Output, teal for Evaluation
- Use clear arrows and moving dots
- Make “ML-Enhanced FAQ Retrieval” visually important with a subtle glow
- Do not overload with tiny text
- Keep everything readable from a distance

Output:
Return one complete polished HTML file with embedded CSS and JavaScript.
The final presentation should contain exactly 3 slides.