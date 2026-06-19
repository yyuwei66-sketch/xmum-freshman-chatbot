import type { ChapterStepProps } from "../../registry/types";
import "./CombinedLayer.css";

export default function CombinedLayer({ step }: ChapterStepProps) {
  if (step === 0) {
    return (
      <section className="cl-scene scene-pad">
        <div className="cl-hero-content">
          <div className="cl-hero-grid">
            <div>
              <p className="kicker">AIT103 · XMUM Freshman FAQ Chatbot</p>
              <h1 className="cl-title">
                Combined
                <span>NLP Layer</span>
              </h1>
            </div>
            <div className="cl-input-card card">
              <span className="label-mono">RAW USER INPUT</span>
              <p>Where is the Wi-Fi office, please???</p>
              <div className="cl-noise">
                <span>mixed case</span>
                <span>extra punctuation</span>
                <span>polite filler</span>
              </div>
            </div>
          </div>
          <div className="cl-bottom-line">
            <span>Text Preprocessing</span>
            <span className="cl-dot" />
            <span>Rule-Based Intent Detection</span>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="cl-scene scene-pad">
        <p className="kicker">Where it sits</p>
        <h2 className="cl-branch-title">Intent detection splits the flow in two.</h2>
        <div className="cl-branch-flow">
          <div className="cl-branch-source card">
            <span className="label-mono">FRONT DOOR</span>
            <strong>User question</strong>
          </div>

          <div className="cl-flow-arrow" aria-hidden="true">→</div>

          <div className="cl-layer-card card">
            <span className="label-mono">COMBINED NLP LAYER</span>
            <div className="cl-layer-stage">
              <span>01</span>
              <strong>Preprocessing</strong>
            </div>
            <div className="cl-stage-arrow" aria-hidden="true">↓</div>
            <div className="cl-layer-stage">
              <span>02</span>
              <strong>Intent Detection</strong>
            </div>
          </div>

          <svg className="cl-branch-lines" viewBox="0 0 140 360" aria-hidden="true">
            <path d="M0 282 C60 282 70 78 140 78" />
            <path d="M0 282 C55 282 80 282 140 282" />
            <circle cx="7" cy="282" r="7" />
          </svg>

          <div className="cl-outcomes">
            <div className="cl-outcome card">
              <span className="label-mono">RULE MATCH</span>
              <strong>Direct Reply</strong>
              <p>small talk → fixed response</p>
            </div>
            <div className="cl-outcome card">
              <span className="label-mono">FAQ QUERY</span>
              <strong>FAQ Route</strong>
              <p>ML category → retrieval answer</p>
            </div>
          </div>
        </div>
    </section>
  );
}
