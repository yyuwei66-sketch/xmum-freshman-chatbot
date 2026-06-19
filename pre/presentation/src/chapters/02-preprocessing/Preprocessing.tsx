import type { ChapterStepProps } from "../../registry/types";
import "./Preprocessing.css";

const sourceSentence = "Where's the Wi-Fi office, please???";
const normalizedSentence = "where's the wifi office please";
const processTokens = ["where", "is", "the", "wifi", "office", "please"];
const stopwords = new Set(["is", "the", "please"]);

function ProcessTrail({ active }: { active: number }) {
  const stageClass = (index: number) =>
    `pp-process-stage card ${index === active ? "is-active" : ""} ${
      index < active ? "is-complete" : ""
    } ${index > active ? "is-future" : ""}`;

  return (
    <div className="pp-process">
      <div className="pp-process-source card">
        <span className="label-mono">RAW SENTENCE</span>
        <strong>{sourceSentence}</strong>
      </div>

      <div className="pp-process-grid">
        <div className={stageClass(0)}>
          <div className="pp-process-head">
            <span>01</span>
            <strong>Normalize</strong>
          </div>
          <div className="pp-stage-content pp-normalized-output">
            {normalizedSentence}
          </div>
          <p>lowercase · trim punctuation · remove hyphen</p>
        </div>

        <div className={stageClass(1)}>
          <div className="pp-process-head">
            <span>02</span>
            <strong>Tokenize</strong>
          </div>
          <div className="pp-stage-content pp-mini-chips">
            {processTokens.map((token, index) => (
              <span className={index < 2 ? "is-expanded" : ""} key={`${token}-${index}`}>
                {token}
              </span>
            ))}
          </div>
          <p className="pp-split-note">where's → where + is</p>
        </div>

        <div className={stageClass(2)}>
          <div className="pp-process-head">
            <span>03</span>
            <strong>Remove</strong>
          </div>
          <div className="pp-stage-content pp-mini-chips">
            {processTokens.map((token, index) => (
              <span className={stopwords.has(token) ? "is-removed" : "is-kept"} key={`${token}-${index}`}>
                {token}
              </span>
            ))}
          </div>
          <p>drop low-information words</p>
        </div>

        <div className={stageClass(3)}>
          <div className="pp-process-head">
            <span>04</span>
            <strong>Stem lightly</strong>
          </div>
          <div className="pp-stage-content pp-final-output">where wifi office</div>
          <p>already base forms · keep meaning intact</p>
        </div>
      </div>
    </div>
  );
}

export default function Preprocessing({ step }: ChapterStepProps) {
  if (step <= 3) {
    const kickers = [
      "Text Normalization",
      "Tokenization",
      "Stopword Removal",
      "Conservative Stemming",
    ];
    const titles = [
      "Start one continuous cleaning path.",
      "Expand the contraction, then split.",
      "Remove words that do not carry intent.",
      "Keep base forms and preserve meaning.",
    ];
    return (
      <section className="pp-scene scene-pad">
        <p className="kicker">{kickers[step]}</p>
        <h2 className="pp-title">{titles[step]}</h2>
        <ProcessTrail active={step} />
      </section>
    );
  }

  if (step === 4) {
    return (
      <section className="pp-scene scene-pad">
        <p className="kicker">Before / After</p>
        <h2 className="pp-title">The next layer gets a cleaner signal.</h2>
        <div className="pp-before-after">
          <div className="pp-example-card card">
            <span className="label-mono">BEFORE</span>
            <strong>{sourceSentence}</strong>
          </div>
          <div className="pp-arrow">→</div>
          <div className="pp-example-card card is-output">
            <span className="label-mono">AFTER</span>
            <strong>where wifi office</strong>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="pp-scene scene-pad">
      <p className="kicker">Prototype Choice</p>
      <div className="pp-prototype">
        <div className="pp-prototype-main">
          <span className="hero-num">0</span>
          <h2>third-party NLP libraries</h2>
        </div>
        <div className="pp-prototype-note card">
          <span className="label-mono">WHY</span>
          <strong>Lightweight, hand-written rules</strong>
          <p>Customizable for XMUM freshman enquiry patterns.</p>
          <div className="pp-prototype-points">
            <span>No NLP dependency</span>
            <span>Rules stay editable</span>
            <span>Campus-specific vocabulary</span>
          </div>
        </div>
      </div>
    </section>
  );
}
