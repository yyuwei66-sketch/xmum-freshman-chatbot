import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..');
const order = ['yyw', 'yy', 'cmh', 'hyh', 'zjy', 'szs', 'hxy'];

const bridge = (id) => String.raw`
<style id="master-deck-overrides">
  .counter, .progress, .nav-zone, .nav-arrow, .slide-no, .slide-index { display: none !important; }
</style>
<script>
(() => {
  const deckId = ${JSON.stringify(id)};
  const slides = [...document.querySelectorAll('.slide')];
  const setSlide = (nextIndex) => {
    const index = Math.max(0, Math.min(slides.length - 1, Number(nextIndex) || 0));
    slides.forEach((slide, slideIndex) => {
      const active = slideIndex === index;
      slide.classList.toggle('is-active', active);
      slide.classList.toggle('was-before', slideIndex < index);
      slide.setAttribute('aria-hidden', String(!active));
    });
    window.__novaSyncIndex?.(index);
    slides[index]?.focus({ preventScroll: true });
  };
  addEventListener('message', event => {
    if (event.data?.type === 'nova-set-slide') setSlide(event.data.index);
    else if (event.data?.type === 'nova-local-command') window.__novaLocalCommand?.(event.data.command);
  });
  document.addEventListener('keydown', event => {
    const target = event.target;
    if (target instanceof Element && target.closest('input, textarea, select, [contenteditable="true"]')) return;
    const commands = {
      ArrowRight: 'next', ArrowDown: 'next', PageDown: 'next', ' ': 'next',
      ArrowLeft: 'prev', ArrowUp: 'prev', PageUp: 'prev',
      Home: 'home', End: 'end', f: 'fullscreen', F: 'fullscreen'
    };
    const command = commands[event.key];
    if (!command) return;
    const localInteractive = deckId === 'cmh' && document.querySelector('.preprocess.is-active');
    if (localInteractive && (command === 'next' || command === 'prev')) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    parent.postMessage({ type: 'nova-command', command }, '*');
  }, true);
  document.addEventListener('click', event => {
    const target = event.target;
    if (target instanceof Element && target.closest('a, button, input, textarea, select, [contenteditable="true"]')) return;
    if (deckId === 'cmh' && document.querySelector('.preprocess.is-active')) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    parent.postMessage({ type: 'nova-command', command: 'next' }, '*');
  }, true);
})();
</script>`;

const decks = order.map(id => {
  const sourcePath = path.join(root, 'pre', `${id}.html`);
  let html = fs.readFileSync(sourcePath, 'utf8');
  const slideCount = (html.match(/<section\s+class=["'][^"']*\bslide\b/g) || []).length;
  html = html.replaceAll("Number(location.hash.slice(1)) - 1 || 0", '0');
  html = html.replaceAll("if (updateHash) history.replaceState(null, '', `#${index + 1}`);", '');
  html = html.replaceAll("window.addEventListener('hashchange', () => render(0, false));", '');
  html = html.replace('</body>', `${bridge(id)}\n</body>`);
  return { id, slideCount, html };
});

const totalSlides = decks.reduce((sum, deck) => sum + deck.slideCount, 0);
const serialized = JSON.stringify(decks).replaceAll('<\/script', '<\\/script');

const output = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Nova — Complete Team Presentation</title>
  <style>
    :root { color-scheme: dark; --ink: #f4f7fb; --muted: #9aa8b8; --accent: #63e6be; }
    * { box-sizing: border-box; }
    html, body { width: 100%; height: 100%; margin: 0; overflow: hidden; background: #070b10; }
    body { font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    .master-stage { position: fixed; inset: 0; display: grid; place-items: center; background: #070b10; }
    .deck-frame { position: absolute; inset: 0; width: 100%; height: 100%; border: 0; background: #070b10; opacity: 0; pointer-events: none; }
    .deck-frame.is-active { opacity: 1; pointer-events: auto; }
    .edge { position: fixed; z-index: 20; top: 8%; bottom: 8%; width: 7%; border: 0; padding: 0; background: transparent; cursor: pointer; }
    .edge.prev { left: 0; cursor: w-resize; }
    .edge.next { right: 0; cursor: e-resize; }
    .edge:focus-visible { outline: 2px solid var(--accent); outline-offset: -6px; }
    .master-progress { position: fixed; z-index: 30; left: 0; right: 0; bottom: 0; height: 3px; background: rgba(255,255,255,.08); pointer-events: none; }
    .master-progress > span { display: block; width: 0; height: 100%; background: var(--accent); transition: width 220ms ease; }
    .master-counter { position: fixed; z-index: 30; top: 22px; right: 24px; padding: 8px 11px; color: #f4f7fb; background: rgba(7,11,16,.72); border: 1px solid rgba(255,255,255,.14); border-radius: 999px; font: 700 12px/1 ui-monospace, SFMono-Regular, Menlo, monospace; letter-spacing: .08em; backdrop-filter: blur(8px); pointer-events: none; }
    .loading { color: var(--muted); font-size: 14px; letter-spacing: .08em; }
    @media (prefers-reduced-motion: reduce) { .deck-frame, .master-progress > span { transition: none; } }
    @media print {
      @page { size: 16in 9in; margin: 0; }
      html, body { overflow: visible; background: #fff; }
      .edge, .master-progress, .master-counter, .loading { display: none !important; }
      .master-stage { position: static; display: block; }
      .deck-frame { position: static; display: block; width: 16in; height: 9in; opacity: 1; page-break-after: always; }
    }
  </style>
</head>
<body>
  <main class="master-stage" aria-label="Nova complete team presentation">
    <div class="loading">LOADING COMPLETE DECK…</div>
  </main>
  <button class="edge prev" type="button" aria-label="Previous slide"></button>
  <button class="edge next" type="button" aria-label="Next slide"></button>
  <div class="master-counter" aria-live="polite">01 / ${String(totalSlides).padStart(2, '0')}</div>
  <div class="master-progress" aria-hidden="true"><span></span></div>
  <script>
    (() => {
      const decks = ${serialized};
      const stage = document.querySelector('.master-stage');
      const counter = document.querySelector('.master-counter');
      const progress = document.querySelector('.master-progress > span');
      const frames = new Map();
      const total = decks.reduce((sum, deck) => sum + deck.slideCount, 0);
      const locations = decks.flatMap((deck, deckIndex) =>
        Array.from({ length: deck.slideCount }, (_, localIndex) => ({ deckIndex, localIndex }))
      );
      let index = Math.max(0, Math.min(total - 1, Number(location.hash.slice(1)) - 1 || 0));
      let touchStartX = null;

      decks.forEach((deck, deckIndex) => {
        const frame = document.createElement('iframe');
        frame.className = 'deck-frame';
        frame.title = deck.id.toUpperCase() + ' presentation section';
        frame.setAttribute('allow', 'fullscreen');
        frame.srcdoc = deck.html;
        frame.addEventListener('load', () => {
          const current = locations[index];
          if (current.deckIndex === deckIndex) frame.contentWindow.postMessage({ type: 'nova-set-slide', index: current.localIndex }, '*');
        });
        frames.set(deck.id, frame);
        stage.append(frame);
      });
      document.querySelector('.loading')?.remove();

      function render(nextIndex, updateHash = true) {
        index = Math.max(0, Math.min(total - 1, nextIndex));
        const current = locations[index];
        decks.forEach((deck, deckIndex) => frames.get(deck.id).classList.toggle('is-active', deckIndex === current.deckIndex));
        const activeDeck = decks[current.deckIndex];
        frames.get(activeDeck.id).contentWindow?.postMessage({ type: 'nova-set-slide', index: current.localIndex }, '*');
        counter.textContent = String(index + 1).padStart(2, '0') + ' / ' + String(total).padStart(2, '0');
        progress.style.width = (((index + 1) / total) * 100) + '%';
        document.title = activeDeck.id.toUpperCase() + ' · ' + (current.localIndex + 1) + '/' + activeDeck.slideCount + ' — Nova Complete Presentation';
        if (updateHash) history.replaceState(null, '', '#' + (index + 1));
      }

      function enterFullscreen() {
        if (!document.fullscreenElement) stage.requestFullscreen?.().catch(() => {});
        else document.exitFullscreen?.().catch(() => {});
      }

      function navigate(command) {
        const current = locations[index];
        const activeDeck = decks[current.deckIndex];
        if (activeDeck.id === 'cmh' && current.localIndex === 1 && (command === 'next' || command === 'prev')) {
          frames.get(activeDeck.id).contentWindow?.postMessage({ type: 'nova-local-command', command }, '*');
          return;
        }
        if (command === 'next') render(index + 1);
        else if (command === 'prev') render(index - 1);
      }

      document.addEventListener('keydown', event => {
        if (event.target instanceof Element && event.target.closest('input, textarea, select, [contenteditable="true"]')) return;
        if (['ArrowRight', 'ArrowDown', 'PageDown', ' '].includes(event.key)) { event.preventDefault(); navigate('next'); }
        else if (['ArrowLeft', 'ArrowUp', 'PageUp'].includes(event.key)) { event.preventDefault(); navigate('prev'); }
        else if (event.key === 'Home') { event.preventDefault(); render(0); }
        else if (event.key === 'End') { event.preventDefault(); render(total - 1); }
        else if (event.key.toLowerCase() === 'f') { event.preventDefault(); enterFullscreen(); }
      });
      document.querySelector('.edge.prev').addEventListener('click', () => navigate('prev'));
      document.querySelector('.edge.next').addEventListener('click', () => navigate('next'));
      window.addEventListener('hashchange', () => render(Number(location.hash.slice(1)) - 1 || 0, false));
      window.addEventListener('message', event => {
        if (event.data?.type === 'nova-command') {
          const actions = {
            next: () => navigate('next'),
            prev: () => navigate('prev'),
            home: () => render(0),
            end: () => render(total - 1),
            fullscreen: enterFullscreen
          };
          actions[event.data.command]?.();
          return;
        }
        if (event.data?.type !== 'nova-child-slide-change') return;
        const deckIndex = decks.findIndex(deck => deck.id === event.data.deckId);
        if (deckIndex < 0 || !frames.get(event.data.deckId).classList.contains('is-active')) return;
        const offset = decks.slice(0, deckIndex).reduce((sum, deck) => sum + deck.slideCount, 0);
        const reported = offset + Math.max(0, Math.min(decks[deckIndex].slideCount - 1, event.data.index));
        if (reported !== index) render(reported);
      });
      stage.addEventListener('touchstart', event => { touchStartX = event.changedTouches[0]?.clientX ?? null; }, { passive: true });
      stage.addEventListener('touchend', event => {
        if (touchStartX === null) return;
        const distance = (event.changedTouches[0]?.clientX ?? touchStartX) - touchStartX;
        touchStartX = null;
        if (Math.abs(distance) >= 48) render(index + (distance < 0 ? 1 : -1));
      }, { passive: true });
      render(index, false);
    })();
  <\/script>
</body>
</html>`;

fs.writeFileSync(path.join(root, 'presentation.html'), output);
console.log(`Merged ${decks.length} decks and ${totalSlides} slides into presentation.html`);
