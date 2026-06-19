import type { Narration } from "../../registry/types";

export const narrations: Narration[] = [
  "After preprocessing, rule-based intent detection checks the easy cases first.",
  'If the input is "hi", "thanks", "bye", "who are you", or "help", the chatbot can answer directly. No FAQ retrieval is needed.',
  'Then it checks FAQ templates. "Where is..." maps to location. "How can I..." maps to procedure. "Who should I contact..." maps to contact. "When is the deadline..." maps to deadline.',
  "If none of those rules match, the query continues to the ML classifier and retrieval-based answer matching.",
];
