import type { ChapterStepProps } from "../../registry/types";
import "./WhyMatters.css";

export default function WhyMatters({ step }: ChapterStepProps) {
  if (step === 0) {
    return (
      <section className="wm-scene scene-pad">
        <p className="kicker">Why This Layer Matters</p>
        <div className="wm-filter">
          <span className="hero-num">01</span>
          <div className="wm-filter-copy">
            <h2>First filter and router</h2>
            <div className="wm-filter-facts">
              <span>standardize input</span>
              <span>catch easy intents</span>
              <span>route complex queries</span>
            </div>
          </div>
          <div className="wm-filter-line" />
        </div>
      </section>
    );
  }

  if (step === 1) {
    return (
      <section className="wm-scene scene-pad">
        <p className="kicker">Noise Reduction</p>
        <h2 className="wm-title">Less noise before the ML classifier.</h2>
        <div className="wm-lanes">
          <div className="wm-lane card">
            <span className="label-mono">SPELLING VARIANTS</span>
            <strong>Wi-Fi</strong>
            <strong>wifi</strong>
            <strong>wi fi</strong>
          </div>
          <div className="wm-lane card is-clean">
            <span className="label-mono">CONSISTENT SIGNAL</span>
            <strong>wifi</strong>
          </div>
        </div>
      </section>
    );
  }

  if (step === 2) {
    return (
      <section className="wm-scene scene-pad">
        <p className="kicker">Stability</p>
        <h2 className="wm-title">Cleaner input supports the whole FAQ pipeline.</h2>
        <div className="wm-stability">
          <div className="wm-stage card">Preprocessed query</div>
          <div className="wm-flow-arrow">→</div>
          <div className="wm-stage card">Category classification</div>
          <div className="wm-flow-arrow">→</div>
          <div className="wm-stage card">Answer retrieval</div>
        </div>
      </section>
    );
  }

  return (
    <section className="wm-scene scene-pad wm-close">
      <p className="kicker">Closing</p>
      <blockquote>
        Although this module is simple, it is the foundation that makes the whole FAQ chatbot more stable and controllable.
      </blockquote>
      <div className="wm-close-values">
        <span>Lightweight</span>
        <span>Explainable</span>
        <span>Campus-ready</span>
      </div>
    </section>
  );
}
