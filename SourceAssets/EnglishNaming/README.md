# English Naming Migration V0.01

작성자 송예찬 · 2026-11-08

User-requested ASCII English hierarchy names. Scene filenames and asset GUIDs were already English and are unchanged.

inventory.py performs a read-only path/serialized-name scan. Survey.cs recorded all13 native scenes and saved backups of the two affected scenes. prepare.py saved6,541 file hashes and the naming policy. plan.py produced1,778 ID-based renames; append_ascii.py added21 corridor names containing arrow symbols, for1,799 total. Apply.cs edits through Unity, checks animation bindings, saves/reloads and compares22,473 serialized object/component snapshots with GameObject names normalized to their original values.

Do not rerun Survey, prepare or plan against the final state; they describe the original baseline. Apply accepts only the recorded old/new names. update_tools.py is one-time: it migrated current review paths/layout names while retaining historical snapshots and one-shot generation sources. Previous generators must not be reapplied to the current scene without adapting their naming rules.

Play.cs/Scenes.cs provide the two-scene smoke check and restore saved editor state. report.py verifies file preservation and writes the review. Current report: Docs/검수/2026-11-08_EnglishNaming/review.md.

- V0.01 (2026-11-08): Naming migration and preservation/Play validation. 송예찬.
