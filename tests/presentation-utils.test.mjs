import { test } from "node:test";
import assert from "node:assert/strict";
import {
  manifestUrl,
  audioUrl,
  pickInitialSlug,
  flattenChunks,
} from "../presentation-utils.js";

test("manifestUrl builds a per-presentation manifest path", () => {
  assert.equal(manifestUrl("intro"), "audio/intro/manifest.json");
});

test("manifestUrl encodes slugs with characters unsafe in a URL", () => {
  assert.equal(
    manifestUrl("Job, Title (ID: 5)"),
    "audio/Job%2C%20Title%20(ID%3A%205)/manifest.json",
  );
});

test("audioUrl builds an encoded per-chunk audio path", () => {
  assert.equal(audioUrl("intro", "001.wav"), "audio/intro/001.wav");
  assert.equal(
    audioUrl("Job, Title", "001.wav"),
    "audio/Job%2C%20Title/001.wav",
  );
});

test("pickInitialSlug prefers the saved slug when it still exists", () => {
  const list = [{ slug: "a" }, { slug: "b" }];
  assert.equal(pickInitialSlug(list, "b"), "b");
});

test("pickInitialSlug falls back to the first presentation when the saved slug is gone", () => {
  const list = [{ slug: "a" }, { slug: "b" }];
  assert.equal(pickInitialSlug(list, "missing"), "a");
});

test("pickInitialSlug falls back to the first presentation when nothing was saved", () => {
  const list = [{ slug: "a" }, { slug: "b" }];
  assert.equal(pickInitialSlug(list, null), "a");
});

test("pickInitialSlug returns null when there are no presentations", () => {
  assert.equal(pickInitialSlug([], "a"), null);
});

test("flattenChunks flattens sections in order and annotates position", () => {
  const manifest = {
    sections: [
      { title: "Opening", chunks: [{ id: "001" }, { id: "002" }] },
      { title: "Closing", chunks: [{ id: "003" }] },
    ],
  };
  const chunks = flattenChunks(manifest);
  assert.equal(chunks.length, 3);
  assert.deepEqual(
    chunks.map((c) => [c.id, c.sectionTitle, c.sectionIndex, c.chunkIndex]),
    [
      ["001", "Opening", 0, 0],
      ["002", "Opening", 0, 1],
      ["003", "Closing", 1, 0],
    ],
  );
});

test("flattenChunks returns an empty list for a manifest with no sections", () => {
  assert.deepEqual(flattenChunks({ sections: [] }), []);
});
