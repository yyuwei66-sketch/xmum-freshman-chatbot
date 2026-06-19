import type { ChapterDef } from "./types";
import CombinedLayer from "../chapters/01-combined-layer/CombinedLayer";
import { narrations as combinedLayerNarrations } from "../chapters/01-combined-layer/narrations";
import Preprocessing from "../chapters/02-preprocessing/Preprocessing";
import { narrations as preprocessingNarrations } from "../chapters/02-preprocessing/narrations";
import RuleIntent from "../chapters/03-rule-intent/RuleIntent";
import { narrations as ruleIntentNarrations } from "../chapters/03-rule-intent/narrations";
import WhyMatters from "../chapters/04-why-matters/WhyMatters";
import { narrations as whyMattersNarrations } from "../chapters/04-why-matters/narrations";

/**
 * Order = order of presentation.
 *
 * Each chapter MUST provide a `narrations: Narration[]` array. Its length
 * is the chapter's step count — there is no `totalSteps` to maintain
 * separately. This guarantees the audio synthesis pipeline, the runtime
 * stepper, and the chapter `.tsx` switch on `step` cannot drift apart.
 *
 * Visual styling (color, fonts) comes entirely from the active theme —
 * chapters never hard-code palette / font names. See THEMES.md.
 */
export const CHAPTERS: ChapterDef[] = [
  {
    id: "combined-layer",
    title: "Combined NLP Layer",
    narrations: combinedLayerNarrations,
    Component: CombinedLayer,
  },
  {
    id: "preprocessing",
    title: "Text Preprocessing",
    narrations: preprocessingNarrations,
    Component: Preprocessing,
  },
  {
    id: "rule-intent",
    title: "Rule-Based Intent Detection",
    narrations: ruleIntentNarrations,
    Component: RuleIntent,
  },
  {
    id: "why-matters",
    title: "Why This Layer Matters",
    narrations: whyMattersNarrations,
    Component: WhyMatters,
  },
];
