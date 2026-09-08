# Teaching illustrations

Remote illustrations are by Sergio Palao, ARASAAC / Gobierno de Aragón,
licensed CC BY-NC-SA. Source and terms: https://arasaac.org/terms-of-use.
The classroom slides display this attribution. Individual source mappings
are in `teaching-sources.json`. Images are linked, not bundled, and require
Internet access when their slide opens. Failed loads offer a retry button.

The small SVG diagrams in `concepts/` are original ENG HUB diagrams generated
by `tools/teaching_diagrams.py`. Existing local lesson images retain their
existing sources. Terms without a reliable image match display as large text.

To refresh source metadata, save the JSON from
https://api.arasaac.org/v1/pictograms/all/en to `tools/cache/arasaac-en.json`,
then run `tools/link_teaching_images.py` and the grade 5/8 polish scripts.
Review new matches visually: exact words can still have unrelated meanings.
