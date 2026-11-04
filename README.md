# opentracker-fw.github.io

The website of OpenTracker, an open, community firmware for the original Polyend Tracker.
It is served by GitHub Pages from the root of the `main` branch, with no build step.

- Plain HTML, CSS and a little vanilla JavaScript. No frameworks, trackers or analytics. The two
  typefaces (Syne, Space Mono) come from Google Fonts; without them the pages fall back to system
  fonts, so they also work offline: open `index.html` from disk. No JavaScript is needed to read
  anything: the folded parts are `<details>`.
- Binaries are not committed. They are attached to the GitHub Releases of this repository
  (`v2.2.3`, `v2.2.4`, `v2.2.5`, `v3.0.0-preview`), and the pages link to
  `https://github.com/opentracker-fw/opentracker-fw.github.io/releases/download/<tag>/<file>`.

## Layout

| Path | What it is |
|---|---|
| `index.html` | home: the hero with the stable download and the four flavour cards; below, the stable release, one fold per 3.0 flavour (synths, effects, files, checksum, install steps, screens), release notes, the video and the install / recovery folds |
| `images.html` | the 3.0 images and the synth / effect picker |
| `modules.html` | one card per synth and effect module |
| `downloads.html` | releases with assets, SHA256 values and release notes; patch packs; the manual |
| `404.html` | page not found |
| `assets/` | `style.css`, `picker.js`, `site.js` (opens the fold a link points at), `video.js`, `favicon.svg` and the generated `data.js` |
| `assets/shots/` | simulator screenshots (800 x 480) used on the home page |
| `notes/<tag>.md` | release notes, used for the GitHub release and shown on `downloads.html` |
| `tools/build.py` | regenerates the marked blocks (`<!-- GEN:... -->`) and `assets/data.js`; can re-stage the 3.0 assets |
| `tools/art.py` | the old flavour illustrations (inline SVG); not used by the current pages, whose step-pattern motif is drawn by `build.py` (`PATTERNS`) |

## Updating

Release files are staged in `../opentracker-fw.github.io-assets/<tag>/`, each folder with a
`SHA256SUMS`. After the 3.0 images are rebuilt, re-stage them and regenerate the pages in one
command:

```
python3 -I tools/build.py --profiles ../ReversedPolytracker-3x/reimpl/profiles \
                          --assets ../opentracker-fw.github.io-assets \
                          --stage-from ../ReversedPolytracker/releases \
                          [--tester-zip PATH]
```

Without `--stage-from` it only regenerates the pages from what is staged. Commit the changed
pages: the generated blocks and `assets/data.js` are committed, so Pages serves them as they are.

OpenTracker is not affiliated with, endorsed by or supported by Polyend.
