import type { ChapterStepProps } from "../../registry/types";
import "./RuleIntent.css";

export default function RuleIntent({ step }: ChapterStepProps) {
  if (step === 0) {
    return (
      <section className="ri-scene scene-pad">
        <p className="kicker">Rule-Based Intent Detection</p>
        <h2 className="ri-title">Check the obvious routes before retrieval.</h2>
        <div className="ri-gate card">
          <span className="label-mono">USER QUERY</span>
          <strong>Can this be answered immediately?</strong>
          <div className="ri-gate-routes">
            <span>Direct reply</span>
            <span>FAQ category</span>
            <span>ML + retrieval</span>
          </div>
          <div className="ri-gate-line" />
        </div>
      </section>
    );
  }

  if (step === 1) {
    const intents = ["hi", "thanks", "bye", "who are you", "help"];
    return (
      <section className="ri-scene scene-pad">
        <p className="kicker">Small Talk</p>
        <h2 className="ri-title">These do not need FAQ retrieval.</h2>
        <div className="ri-smalltalk">
          {intents.map((intent) => (
            <span className="ri-intent-chip" key={intent}>
              {intent}
            </span>
          ))}
          <div className="ri-fixed card">
            <span className="label-mono">YES</span>
            <strong>fixed reply</strong>
          </div>
        </div>
      </section>
    );
  }

  if (step === 2) {
    const templates = [
      ['"where is..."', "location"],
      ['"how can I..."', "procedure"],
      ['"who should I contact..."', "contact"],
      ['"when is the deadline..."', "deadline"],
    ];
    return (
      <section className="ri-scene scene-pad">
        <p className="kicker">FAQ Templates</p>
        <h2 className="ri-title">Common openings become category routes.</h2>
        <div className="ri-template-grid">
          {templates.map(([query, category]) => (
            <div className="ri-template-card card" key={query}>
              <span>{query}</span>
              <strong>{category}</strong>
            </div>
          ))}
        </div>
      </section>
    );
  }

  return (
    <section className="ri-scene scene-pad">
      <p className="kicker">Decision Tree</p>
      <h2 className="ri-title">Rules handle clear cases. ML handles the rest.</h2>
      <div className="ri-tree">
        <div className="ri-tree-node card ri-tree-root">User query</div>
        <div className="ri-tree-node card ri-tree-q1">Small talk?</div>
        <div className="ri-tree-node card ri-tree-a1">Fixed reply</div>
        <div className="ri-tree-node card ri-tree-q2">FAQ template?</div>
        <div className="ri-tree-node card ri-tree-a2">Route category</div>
        <div className="ri-tree-node card ri-tree-a3">ML classifier + retrieval</div>
        <svg className="ri-tree-lines" viewBox="0 0 1000 470" aria-hidden="true">
          <path d="M500 50 L500 130" />
          <path d="M500 210 L270 300" />
          <path d="M500 210 L500 300" />
          <path d="M500 380 L320 440" />
          <path d="M500 380 L720 440" />
        </svg>
      </div>
    </section>
  );
}
