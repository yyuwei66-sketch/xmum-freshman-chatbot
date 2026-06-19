User input is messy.
The Combined NLP Layer cleans it first, then routes it fast.

---

The path is: user input, preprocessing, intent detection, then either a direct reply or the FAQ route.

---

First, text normalization.
We lowercase the sentence, remove extra punctuation and spaces, and normalize Wi-Fi to wifi while keeping the contraction for the next step.

---

Then tokenization.
The contraction "where's" is expanded into "where" and "is", before the sentence is split into word units.

---

Next, stopword removal.
Words like "the", "is", and "please" usually do not carry the main intent.

---

Finally, conservative stemming.
The remaining words are checked conservatively. Here, "where", "wifi", and "office" are already suitable base forms, so the meaning stays intact.

---

So "Where's the Wi-Fi office, please???" becomes "where wifi office".
That is much easier for the next layer to handle.

---

This part is a lightweight hand-written prototype.
We did not depend on third-party NLP libraries, so the rules can be customized for XMUM scenarios.

---

After preprocessing, rule-based intent detection checks the easy cases first.

---

If the input is "hi", "thanks", "bye", "who are you", or "help", the chatbot can answer directly.
No FAQ retrieval is needed.

---

Then it checks FAQ templates.
"Where is..." maps to location.
"How can I..." maps to procedure.
"Who should I contact..." maps to contact.
"When is the deadline..." maps to deadline.

---

If none of those rules match, the query continues to the ML classifier and retrieval-based answer matching.

---

This layer matters because it is the first filter and router of the chatbot.

---

It reduces noise before ML classification.
It also makes spelling variants more consistent, like Wi-Fi, wifi, and wi fi.

---

That stability helps category classification and answer retrieval work better.

---

Although this module is simple, it is the foundation that makes the whole FAQ chatbot more stable and controllable.
