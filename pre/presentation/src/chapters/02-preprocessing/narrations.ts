import type { Narration } from "../../registry/types";

export const narrations: Narration[] = [
  "First, text normalization. We lowercase the sentence, remove extra punctuation and spaces, and normalize Wi-Fi to wifi while keeping the contraction for the next step.",
  "Then tokenization. The contraction where's is expanded into where and is, before the full sentence is split into word units.",
  "Next, stopword removal. Words like the, is, and please usually do not carry the main intent.",
  "Finally, conservative stemming checks the remaining tokens. Here, where, wifi, and office are already suitable base forms, so the meaning stays intact.",
  'So "Where\'s the Wi-Fi office, please???" becomes "where wifi office". That is much easier for the next layer to handle.',
  "This part is a lightweight hand-written prototype. We did not depend on third-party NLP libraries, so the rules can be customized for XMUM scenarios.",
];
