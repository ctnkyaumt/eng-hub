# Teaching illustrations

Remote illustrations are by Sergio Palao, ARASAAC / Gobierno de Aragón,
licensed CC BY-NC-SA. Source and terms: https://arasaac.org/terms-of-use.
The classroom slides display this attribution. Individual source mappings
are in `teaching-sources.json`. Images are linked, not bundled, and require
Internet access when their slide opens. Failed loads offer a retry button.

The SVG diagrams in `concepts/` are original ENG HUB diagrams generated
by `tools/teaching_diagrams.py` and `tools/concept_scenes.py`. Every nonnumeric
vocabulary card has a picture; abstract terms use illustrated situations.
Existing local lesson images retain their existing sources.

Additional photos come from Wikimedia Commons. Individual authors, file pages
and licences are recorded in `commons-teaching-sources.json` and displayed in
`teaching-credits.html`, linked from the relevant slides. Photos are unchanged
and displayed proportionally. They load only when the slide opens.

To refresh source metadata, save the JSON from
https://api.arasaac.org/v1/pictograms/all/en to `tools/cache/arasaac-en.json`,
then run `tools/link_teaching_images.py`, `tools/complete_teaching_images.py`
and the grade 5/8 polish scripts (`--grade 5` / `--grade 8`).
Review new matches visually: exact words can still have unrelated meanings.
