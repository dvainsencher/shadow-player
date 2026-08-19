import { manifestUrl, audioUrl, pickInitialSlug, flattenChunks } from "./presentation-utils.js";

// Playback speeds offered to the user. The number-key shortcut for each
// speed is just its position in this list (1 = first speed, 2 = second, …),
// so adding or removing a speed doesn't require touching anything else.
const SPEEDS = [0.7, 0.85, 1.0, 1.15, 1.3, 1.5];
const DEFAULT_SPEED = 0.85;
const LAST_SLUG_KEY = "shadow-player:lastSlug";

const $ = (id) => document.getElementById(id);
const audio = new Audio();

const state = {
  presentations: [], // every audio/<slug>/ folder that has a manifest.json
  slug: null, // the currently loaded presentation's folder name
  manifest: null,
  chunks: [], // flattened list of every chunk across all sections
  current: 0, // index into `chunks`
  textHidden: false,
  speed: DEFAULT_SPEED,
};

async function init() {
  bindControls();
  bindKeyboard();

  state.presentations = await fetchPresentations();
  renderPresentationList();

  const savedSlug = localStorage.getItem(LAST_SLUG_KEY);
  const initialSlug = pickInitialSlug(state.presentations, savedSlug);
  if (!initialSlug) {
    showNoPresentationsMessage();
    return;
  }
  await loadPresentation(initialSlug);
}

async function fetchPresentations() {
  const response = await fetch("/api/presentations", { cache: "no-store" });
  if (!response.ok) throw new Error("Could not list presentations.");
  return response.json();
}

function renderPresentationList() {
  const list = $("presentations");
  list.innerHTML = "";
  state.presentations.forEach((presentation) => {
    const link = document.createElement("button");
    link.className = "presentation-link";
    link.dataset.slug = presentation.slug;
    link.classList.toggle("active", presentation.slug === state.slug);

    const title = document.createElement("span");
    title.className = "presentation-title";
    title.textContent = presentation.title;

    const meta = document.createElement("span");
    meta.className = "presentation-meta";
    meta.textContent = presentation.chunks === 1 ? "1 chunk" : `${presentation.chunks} chunks`;

    link.append(title, meta);
    link.onclick = () => loadPresentation(presentation.slug).catch(reportError);
    list.append(link);
  });
}

function updatePresentationActiveState() {
  document.querySelectorAll(".presentation-link").forEach((link) => {
    link.classList.toggle("active", link.dataset.slug === state.slug);
  });
}

function showNoPresentationsMessage() {
  $("meta").textContent = "";
  $("reader").textContent =
    'No generated presentations found. Run "./generate.sh your-file.txt" then refresh.';
}

async function loadPresentation(slug) {
  const response = await fetch(manifestUrl(slug), { cache: "no-store" });
  if (!response.ok) throw new Error(`Could not load presentation "${slug}".`);

  state.slug = slug;
  state.manifest = await response.json();
  state.speed = state.manifest.speed || DEFAULT_SPEED;
  state.chunks = flattenChunks(state.manifest);

  localStorage.setItem(LAST_SLUG_KEY, slug);
  updatePresentationActiveState();

  renderMeta();
  renderSpeedButtons();
  renderNav();
  renderReader();
  selectChunk(0);
}

function renderMeta() {
  const { sections } = state.manifest;
  $("meta").textContent =
    `${sections.length} sections · ${state.chunks.length} chunks · ` +
    `${state.manifest.voice} · generated at ${state.manifest.speed}×`;
}

function renderSpeedButtons() {
  const container = $("speedButtons");
  container.innerHTML = "";
  SPEEDS.forEach((speed, index) => {
    const button = document.createElement("button");
    button.textContent = `${speed}×`;
    button.dataset.speed = String(speed);
    button.title = `Press ${index + 1}`;
    button.classList.toggle("active-speed", speed === state.speed);
    button.onclick = () => setSpeed(speed);
    container.append(button);
  });
  // Keep the keyboard hint in sync with SPEEDS instead of hardcoding a count.
  $("speedHint").textContent = `1-${SPEEDS.length} set speed`;
}

function setSpeed(speed) {
  state.speed = speed;
  audio.playbackRate = speed;
  document.querySelectorAll("#speedButtons button").forEach((button) => {
    button.classList.toggle("active-speed", Number(button.dataset.speed) === speed);
  });
}

function renderNav() {
  const nav = $("sections");
  nav.innerHTML = "";
  state.manifest.sections.forEach((section) => {
    const title = document.createElement("div");
    title.className = "section-title";
    title.textContent = section.title;
    nav.append(title);

    section.chunks.forEach((chunk, chunkIndex) => {
      const link = document.createElement("button");
      link.className = "chunk-link";
      link.textContent = `Chunk ${chunkIndex + 1}`;
      link.onclick = () => selectChunk(state.chunks.findIndex((c) => c.id === chunk.id));
      nav.append(link);
    });
  });
}

function renderReader() {
  const reader = $("reader");
  reader.innerHTML = "";
  state.chunks.forEach((chunk, index) => {
    const el = document.createElement("div");
    el.className = "chunk";
    el.dataset.index = String(index);
    el.textContent = chunk.text;
    el.onclick = () => selectChunk(index);
    reader.append(el);
  });
}

function selectChunk(index) {
  if (!state.chunks.length) return;
  state.current = Math.max(0, Math.min(index, state.chunks.length - 1));

  audio.pause();
  audio.currentTime = 0;
  audio.src = audioUrl(state.slug, state.chunks[state.current].audio);
  audio.playbackRate = state.speed;

  updateUI();
}

function updateUI() {
  document.querySelectorAll(".chunk").forEach((el, i) => {
    el.classList.toggle("active", i === state.current);
    el.classList.toggle("dim", i !== state.current);
  });
  document.querySelectorAll(".chunk-link").forEach((el, i) => {
    el.classList.toggle("active", i === state.current);
  });

  const chunk = state.chunks[state.current];
  const totalInSection = state.manifest.sections[chunk.sectionIndex].chunks.length;
  $("position").textContent =
    `${chunk.sectionTitle} · Chunk ${chunk.chunkIndex + 1}/${totalInSection} · ` +
    `${state.current + 1}/${state.chunks.length}`;

  document
    .querySelector(`.chunk[data-index="${state.current}"]`)
    ?.scrollIntoView({ block: "center", behavior: "smooth" });

  setPlayButtonLabel(false);
}

function setPlayButtonLabel(isPlaying) {
  $("play").textContent = isPlaying ? "⏸ Pause" : "▶ Play";
}

function togglePlayback() {
  if (audio.paused) {
    audio.play();
    setPlayButtonLabel(true);
  } else {
    audio.pause();
    setPlayButtonLabel(false);
  }
}

function repeatChunk() {
  audio.currentTime = 0;
  audio.play();
  setPlayButtonLabel(true);
}

function toggleTextHidden() {
  state.textHidden = !state.textHidden;
  $("reader").classList.toggle("hidden", state.textHidden);
  $("hideBtn").innerHTML = state.textHidden ? "Show text <kbd>H</kbd>" : "Hide text <kbd>H</kbd>";
}

function bindControls() {
  $("play").onclick = togglePlayback;
  $("repeat").onclick = repeatChunk;
  $("prev").onclick = () => selectChunk(state.current - 1);
  $("next").onclick = () => selectChunk(state.current + 1);
  $("hideBtn").onclick = toggleTextHidden;
  audio.onended = () => setPlayButtonLabel(false);
}

const KEY_ACTIONS = {
  " ": () => togglePlayback(),
  r: () => repeatChunk(),
  arrowleft: () => selectChunk(state.current - 1),
  arrowright: () => selectChunk(state.current + 1),
  h: () => toggleTextHidden(),
};

function bindKeyboard() {
  document.onkeydown = (e) => {
    if (["INPUT", "TEXTAREA"].includes(e.target.tagName)) return;

    // Number keys select a speed by position (1 = SPEEDS[0], 2 = SPEEDS[1], ...).
    const asNumber = Number(e.key);
    if (Number.isInteger(asNumber) && asNumber >= 1 && asNumber <= SPEEDS.length) {
      setSpeed(SPEEDS[asNumber - 1]);
      return;
    }

    const key = e.code === "Space" ? " " : e.key.toLowerCase();
    const action = KEY_ACTIONS[key];
    if (action) {
      e.preventDefault();
      action();
    }
  };
}

function reportError(e) {
  $("reader").textContent = e.message;
  console.error(e);
}

init().catch(reportError);
