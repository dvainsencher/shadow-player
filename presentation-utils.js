// Pure, DOM-free helpers for the presentation picker — no browser globals,
// so they're directly unit-testable with Node's built-in test runner
// (see tests/presentation-utils.test.mjs) without any bundler or deps.

// Each generated presentation lives at audio/<slug>/, written by generate.py.
// Slugs come from the server's directory scan, so they're real folder names
// and may contain characters that need URL-encoding (spaces, commas, ...).
export function manifestUrl(slug) {
  return `audio/${encodeURIComponent(slug)}/manifest.json`;
}

export function audioUrl(slug, filename) {
  return `audio/${encodeURIComponent(slug)}/${encodeURIComponent(filename)}`;
}

// Which presentation to load initially: the previously-used one if it's
// still in the current list, otherwise the first (most recently generated).
export function pickInitialSlug(presentations, savedSlug) {
  if (!presentations.length) return null;
  if (savedSlug && presentations.some((p) => p.slug === savedSlug)) return savedSlug;
  return presentations[0].slug;
}

// Flattens a manifest's sections into a single ordered list of chunks, each
// annotated with where it sits (section/chunk index + section title).
export function flattenChunks(manifest) {
  const chunks = [];
  manifest.sections.forEach((section, sectionIndex) => {
    section.chunks.forEach((chunk, chunkIndex) => {
      chunks.push({ ...chunk, sectionIndex, chunkIndex, sectionTitle: section.title });
    });
  });
  return chunks;
}
