# Second Brain — an LLM‑Maintained Personal Knowledge Base

A personal knowledge system in which an AI agent (Claude Code) incrementally **compiles raw, unstructured notes into a heavily interlinked, Wikipedia‑style knowledge base** inside an Obsidian vault. Instead of re‑reading documents on every query, the agent reads each new note once, extracts its key information, and integrates it across the wiki — creating and updating source, entity, and concept pages and weaving bi‑directional links between them.

The result is an assistant that knows your context: rather than answering like a generic chatbot, it reads your own knowledge base and tailors every answer and code snippet to what you've actually studied and built.

> **This repository contains the engine only** — the schema, templates, and example pages — so the architecture can be reused and inspected. The actual personal notes are kept in a private vault and are intentionally not published here. See [Privacy](#privacy).

---

## Architecture — three layers

```
Second-Brain/
├── CLAUDE.md            ← Schema layer: the rules the AI follows
├── raw/                 ← Source layer: immutable original notes (read-only to the AI)
└── wiki/                ← Knowledge layer: AI-generated, interlinked pages
    ├── sources/         ← one page per ingested note (thesis, key claims, data)
    ├── entities/        ← one page per person, org, product, or tool
    ├── concepts/        ← one page per idea or framework
    ├── templates/       ← page templates for each type
    ├── README.md        ← Map of Content (maintained by the AI)
    └── activity_log.md  ← log of ingestions, to avoid duplicate work
```

1. **Raw sources** — the immutable source of truth. The AI may only *read* here; it never edits, summarises, or deletes original notes.
2. **The wiki** — fully AI‑managed. Organised strictly *by page type* (sources / entities / concepts), not by topic, so cross‑topic connections surface naturally.
3. **The schema (`CLAUDE.md`)** — the configuration that turns a generic assistant into a disciplined wiki maintainer: it defines directory rules, ingestion and health‑check workflows, linking conventions, and a signature tag.

## Design decisions worth highlighting

- **Anti‑reductionism / 1:1 verbatim rule.** The biggest risk with an LLM compiler is that it "helpfully" summarises away technical detail. The schema forbids this: step‑by‑step methods, prompts, and code must be transferred word‑for‑word so every page stays **copy‑paste functional**.
- **One page per source.** Maximum granularity — no multi‑source merge bloat — which keeps backlinks precise.
- **Bi‑directional linking.** Pages connect with Obsidian `[[wikilinks]]`; missing targets are stubbed automatically, so the graph stays navigable.
- **Idempotent ingestion.** An `activity_log.md` records what's already been processed, so re‑runs don't duplicate work.
- **`(C)` signature.** Every AI‑written page is tagged, making it trivial to tell machine‑generated pages from hand edits.

## Workflows

| Command | What the agent does |
|---|---|
| `Ingest the new files in raw/` | Diffs `raw/` against the activity log, creates one verbatim source page per new file, injects wikilinks, updates the Map of Content, and logs the run. |
| `!lint` (health check) | Finds orphaned pages and dead links, detects pages filed under the wrong type, flags contradictions between older and newer sources, and proposes fixes before applying them. |
| `What do we know about <topic>?` | Reads the index and relevant pages and answers with `[[wikilink]]` citations — falling back to general knowledge when the wiki has nothing on the topic. |

## Use cases

The same engine works for any kind of knowledge that compounds over time:

- **A context‑aware coding & study assistant.** Because the agent reads your own notes, it stops giving generic web answers and instead tailors code and explanations to the methods, tools, and level you've actually recorded. If a topic isn't in the wiki, it falls back to general knowledge instead of getting stuck.
- **Build from theory you've already captured.** You may not have a finished script saved, but if your notes explain *how* something works, the agent can generate the Python/Bash/etc. from scratch — following the exact approach you studied rather than a random one off the internet.
- **Deep research over weeks or months.** Ingest every paper, article, and report as you find it; the wiki builds an evolving synthesis with entity and concept pages, so a question that spans five sources is already answered because the synthesis was done incrementally.
- **Course & certification notes.** Feed in each lecture or exercise; the wiki tracks how concepts build on each other and flags when later material updates earlier notes, giving you a personal reference organised by how *you* learned it.
- **Project knowledge base.** Centralise scattered notes from different tools (docs, clipped pages, course material) into one queryable place, with cross‑links surfacing connections you'd otherwise forget.

## How this one was built

- Exported a large personal Notion workspace (400+ notes spanning security, DevOps, AI, and personal research) into clean markdown under `raw/`.
- Pointed Claude Code at the vault with the `CLAUDE.md` schema and ran a full ingestion, producing per‑source verbatim pages plus synthesised concept and entity pages, all cross‑linked.
- Used `!lint` passes to repair broken links and re‑file mis‑categorised pages as the vault grew.

## Try the example

This repo ships a tiny, fictional example (`raw/example-source.md` → a source, entity, and concept page) so you can see the structure end‑to‑end. To run it on your own notes:

1. Install [Obsidian](https://obsidian.md) and [Claude Code](https://www.claude.com/product/claude-code).
2. Drop your markdown notes into `raw/`.
3. Open the folder in Claude Code and run: `Ingest the new files in raw/`.
4. Open the vault in Obsidian and explore the graph view.

## Privacy

Only the **engine** (`CLAUDE.md`, `wiki/templates/`, and example pages) is published. The real `raw/` notes and the generated `wiki/sources|entities|concepts` pages are kept in a **private** vault, because a personal knowledge base of this kind necessarily contains confidential material. If you fork this, keep your own `raw/` out of any public repository (add it to `.gitignore`).
