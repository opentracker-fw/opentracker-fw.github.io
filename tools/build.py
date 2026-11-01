#!/usr/bin/env python3
"""Regenerate the generated parts of the site.

The site itself is static: GitHub Pages serves the committed files as they are. This
script only rewrites the blocks between <!-- GEN:name --> and <!-- /GEN:name --> markers
and writes assets/data.js. Run it after a profile, a module or a release asset changes:

    python3 -I tools/build.py --profiles ../ReversedPolytracker-3x/reimpl/profiles \
                              --assets ../opentracker-fw.github.io-assets \
                              [--stage-from ../ReversedPolytracker/releases [--tester-zip ZIP]]

--profiles  the firmware's reimpl/profiles directory (the *.toml build profiles)
--assets    the staged release assets, one folder per tag with a SHA256SUMS file
--stage-from  re-stage the 3.0 preview images and patch zips from the release folders first
              (each folder's own SHA256SUMS is checked, a new combined one is written)
"""

import argparse
import html
import json
import os
import re
import sys
import tomllib

ORG = "opentracker-fw"
SITE_REPO = f"{ORG}.github.io"
DL = f"https://github.com/{ORG}/{SITE_REPO}/releases/download"
REPO = {
    "synths": f"https://github.com/{ORG}/opentracker-synths/tree/main",
    "fx": f"https://github.com/{ORG}/opentracker-fx/tree/main",
}

STABLE_TAG = "v2.2.3"
STABLE_VERSION = "2.2.3"
STABLE_IMAGE = "PolyendTrackerOTv223.ptf"
STABLE_DATE = "2026-10-30"
PREVIEW_VERSION = "3.0.0 preview"
FW_REPO = f"https://github.com/{ORG}/opentracker"
PREVIEW_TAG = "v3.0.0-preview"

# The firmware, synths and fx repos are private for now. While this is False the site
# shows no links to them: no "Code" footer column, no module "Source" rows, no profile or
# branch links, and bug reports go to the site repo's issue tracker.
PUBLIC_REPOS = False
ISSUES = f"{FW_REPO}/issues" if PUBLIC_REPOS else f"https://github.com/{ORG}/{SITE_REPO}/issues"
# The public 2.x source that people can fork.
CONTRIBUTE = "https://github.com/sandlbn/polyend-tracker-re/tree/v2"

# The published 3.0 images. Mini (m), No-FM (n), full (v) and core (c) are not published.
IMAGES = [
    ("a", "classic", "Classic", "Analog-style synths: acid, poly pads, mono basses and leads."),
    ("i", "idm", "IDM", "FM, wavetable FM, drums and acid."),
    ("t", "techno", "Techno", "T-Type drums, acid, basses and stabs, drive / bitcrush and a tempo-synced echo."),
    ("r", "retro", "Retro", "Chip-style synths: 8-bit computer and handheld voices, buzz tones, console FM and a chip DAC on the mix."),
]

# One-line vibe per flavour (home page boxes) and the order they are shown in.
VIBE = {
    "techno": "Concrete, strobes and a kick that doesn't stop: drums, acid, drive and a tempo-synced echo.",
    "idm": "Broken grids and bent FM: wavetables, four-operator FM, drums and acid.",
    "classic": "Warm and analog in style: poly pads, mono basses, duophonic leads and tape.",
    "retro": "Blips, buzz and fast arps: four chip-style synths, a chip DAC on the mix and a tempo-synced echo.",
    "mini": "The five Mini synths, so every Mini project plays.",
    "nofm": "Every synth but the FM ones, with both drum synths.",
}
FEATURED = ["techno", "idm", "classic", "retro"]

# Per-flavour section on the home page: short feature cards and simulator screenshots
# (assets/shots/*.png, 800x480, taken with the headless simulator built for that profile).
TAGLINE = {
    "techno": "Built for the warehouse.",
    "idm": "Built for the bedroom lab.",
    "classic": "Built for the studio wall of knobs.",
    "retro": "Built for the arcade.",
}
FEATURES = {
    "techno": [
        ("T-Type drums", "One patch is a whole kit: kick, snare, clap, three toms, rim, cowbell, hats, crash and ride, each drum with three Characters."),
        ("Dirt", "Drive and bitcrush on the whole mix: four shapers, bits, sample rate, tone."),
        ("Echo", "A dub echo locked to the song tempo, with ping-pong and duck."),
        ("Acid and stabs", "ACD, FAT, JU6 and D-Type for basses, leads and chords."),
    ],
    "idm": [
        ("WTFM", "Two-operator wavetable FM with three feedback paths: e-pianos, bells, mallets."),
        ("FM4", "Four operators, 8 algorithms, an envelope per operator."),
        ("PERC", "A drum machine with one drum per note and tunable toms."),
        ("Chorus and Tape", "A stereo chorus and a tape stage on the whole mix."),
    ],
    "classic": [
        ("CS-Type", "Two layers per note, each with its own filters and envelopes; Touch and Ribbon on the macros."),
        ("A-Type", "Duophonic: two oscillators, hard sync, ring mod, sample & hold."),
        ("D-Type", "Three oscillators into a filter that whistles on its own."),
        ("JU6", "A poly with a built-in stereo chorus, saved in every patch."),
    ],
    "retro": [
        ("8-Type", "Three oscillators with ring, sync and the combined waves into a 12 dB multimode filter: leads, basses, chords."),
        ("Hand-Type", "Pulse with sweep, a 4-bit wave or noise, one channel per patch, or a whole drum kit by note."),
        ("B-Type and Arc-Type", "Buzz tones from polynomial counters, and four-operator FM with looping envelopes."),
        ("LoFi", "The mix through a small chip's output: bits, sample rate, uneven DAC steps and a speaker."),
    ],
}
SHOTS = {
    "techno": [
        ("techno-ttype-edit.png", "T-Type: Edit Patch on the kick of OT Kit Deep Boom"),
        ("techno-ttype-kits.png", "Twelve T-Type kits in Load Patch"),
        ("techno-dirt.png", "Dirt on the whole mix (Shift + Master)"),
        ("techno-echo.png", "Echo, synced to the song tempo"),
    ],
    "idm": [
        ("idm-wtfm-edit.png", "WTFM: the two operators of OT Crystal Pad"),
        ("idm-fm4-edit.png", "FM4: Edit Patch, with the four operators, LFO and Global sections"),
        ("pattern-editor.png", "The pattern editor playing an IDM test song"),
    ],
    "classic": [
        ("classic-cstype-edit.png", "CS-Type: layer I oscillator of OT Film Pad"),
        ("classic-atype-edit.png", "A-Type: oscillator 1 of OT Lead 2-Osc"),
        ("classic-dtype-edit.png", "D-Type: oscillator 1 of OT Growl Bass"),
    ],
    "retro": [
        ("retro-eight-edit.png", "8-Type: oscillator 1 of OT Chip Lead"),
        ("retro-arc-edit.png", "Arc-Type: operator 1 of OT Loop Buzz Pad, with a looping envelope"),
        ("retro-hand-edit.png", "Hand-Type: the pulse channel of OT Pulse Lead"),
        ("retro-lofi.png", "LoFi on the whole mix (Shift + Master)"),
    ],
}

# Module facts for the site. The repo folder must match the profile's path.
# patches: patch count in the 3.0.0 preview pack (Patches/<folder>/), None for effects.
MODULES = {
    "ACD1": dict(name="ACD", kind="synth", repo="synths", folder="modules/acd", patches=12,
                 desc="Acid bass and lead: a 24 dB and a ladder-style filter and glide, mono or poly."),
    "FAT1": dict(name="FAT", kind="synth", repo="synths", folder="modules/fat", patches=8,
                 desc="A stack of detuned saws for supersaw pads, leads and basses."),
    "VAP1": dict(name="VAP", kind="synth", repo="synths", folder="modules/vap", patches=16,
                 desc="Virtual-analog poly: morphing oscillators, hard sync, 15 filter types and a 6-slot modulation matrix."),
    "PRC1": dict(name="PERC", kind="synth", repo="synths", folder="modules/perc", patches=16,
                 desc="Drum machine with one drum per note: kick, snare, hats, cymbal, perc and tunable toms."),
    "WTF1": dict(name="WTFM", kind="synth", repo="synths", folder="modules/wtfm", patches=30,
                 desc="Two-operator wavetable FM with three feedback paths: electric pianos, clav, bells, mallets, basses and pads."),
    "FM4S": dict(name="FM4", kind="synth", repo="synths", folder="modules/fm4", patches=0,
                 desc="Four-operator FM: 8 algorithms, feedback, an envelope per operator and an LFO."),
    "JU6S": dict(name="JU6", kind="synth", repo="synths", folder="modules/ju6", patches=12,
                 desc="Poly synth in the style of the classic early-1980s polysynths: saw and pulse with PWM, sub oscillator, noise, "
                      "4-position high-pass, resonant 24 dB low-pass and a built-in stereo chorus (Off, I, II) per slot."),
    "DTY1": dict(name="D-Type", kind="synth", repo="synths", folder="modules/dtype", patches=12,
                 desc="Mono synth in the style of the classic three-oscillator synths of the 1970s: three oscillators, white or pink noise, "
                      "mixer feedback, a self-oscillating 24 dB low-pass, two contours, glide and a mod wheel."),
    "CST1": dict(name="CS-Type", kind="synth", repo="synths", folder="modules/cstype", patches=12,
                 desc="Polysynth in the style of the big two-layer polysynths of the late 1970s: two layers per note, each with its own "
                      "oscillators, filters and envelopes; ring modulator, Brilliance, Touch and Ribbon."),
    "ATY1": dict(name="A-Type", kind="synth", repo="synths", folder="modules/atype", patches=12,
                 desc="Two-oscillator synth in the style of the semi-modular duophonic synths of the 1970s: hard sync, ring modulator or noise, "
                      "sample & hold, 24 or 12 dB low-pass, Keyboard Duo and note priority."),
    "TTY1": dict(name="T-Type", kind="synth", repo="synths", folder="modules/ttype", patches=12,
                 desc="Drum synth in the classic analog drum machine style. One patch is one kit: kick, snare, clap, three toms, rim, "
                      "cowbell, hats, crash and ride, each drum with three Characters and its own sends."),
    "8TY1": dict(name="8-Type", kind="synth", repo="synths", folder="modules/eight", patches=12,
                 desc="Chip-style synth in the style of the 8-bit home computers of the early 1980s: three oscillators (triangle, saw, "
                      "pulse with PWM, noise and the combined waves) with ring and sync, a 12 dB multimode filter with 16 resonance "
                      "steps, Grit, a 16-step ADSR and the CHIP arp, vibrato and slide."),
    "HND1": dict(name="Hand-Type", kind="synth", repo="synths", folder="modules/hand", patches=12,
                 desc="Chip-style synth in the style of a 4-channel handheld console: one patch is one channel (pulse with duty, "
                      "sweep and a second pulse; a 32-step 4-bit wave; or noise) or a whole drum kit by note, with a stepped "
                      "4-bit envelope, Length and the CHIP arp, vibrato and slide."),
    "BTY1": dict(name="B-Type", kind="synth", repo="synths", folder="modules/btype", patches=12,
                 desc="Chip-style synth in the style of the 8-bit computers with polynomial counters: a clock and a divider "
                      "(Free, Coarse or Fine tuning), the buzz distortions, a second channel a few divider steps away, the "
                      "high-pass pair, a 4-bit ADSR and the CHIP arp, vibrato and slide."),
    "ARC1": dict(name="Arc-Type", kind="synth", repo="synths", folder="modules/arc", patches=12,
                 desc="Four-operator FM in the style of the home consoles of the late 1980s: eight algorithms, feedback, "
                      "envelopes that can loop, an LFO, a 9-bit DAC with a ladder character, an Aux square or noise voice "
                      "and the CHIP arp and slide."),
    "TAPE": dict(name="Tape", kind="effect", repo="fx", folder="modules/tape", patches=None,
                 desc="Tape on the whole mix: drive (saturation), head-loss high cut, wow, flutter and mix."),
    "CHOR": dict(name="Chorus", kind="effect", repo="fx", folder="modules/chorus", patches=None,
                 desc="Stereo chorus on the whole mix: rate, depth, width and mix."),
    "DIRT": dict(name="Dirt", kind="effect", repo="fx", folder="modules/dirt", patches=None,
                 desc="Drive and bitcrush on the whole mix: Soft, Hard, Fold and Asym shapers, Bits 4-16, sample-rate reduction, tone and mix."),
    "ECHO": dict(name="Echo", kind="effect", repo="fx", folder="modules/echo", patches=None,
                 desc="Dub-style echo that follows the song tempo: 1/32 to 1/2 with dotted and triplet times, feedback, low cut, tone, "
                      "ping-pong, duck and mix."),
    "LOFI": dict(name="LoFi", kind="effect", repo="fx", folder="modules/lofi", patches=None,
                 desc="The whole mix through a small chip's output: Bits 4-15, a sample-and-hold Rate down to 4 kHz, Ladder "
                      "(uneven DAC steps), Speaker (TV, Handheld, Monitor), Mono and mix."),
}

ASSET_DESC = {
    "PolyendTrackerOTv223.ptf": "Firmware image 2.2.3",
    "OpenTracker-2.2.3-Patches.zip": "Preset pack: 82 patches (ACD, FAT, VAP, WTFM, PERC)",
    "OpenTracker-2.2.3-Projects.zip": "Test songs: copy to /Projects",
    "OpenTracker-2.2.3-Themes.zip": "New: 12 example colour themes, unzip to the card",
    "OpenTracker-2.2.3-Manual.pdf": "User manual for 2.2.3",
    "SHA256SUMS": "Checksums of every file in this release",
}


def _load_art():
    import importlib.util
    here = os.path.dirname(os.path.abspath(__file__))
    spec = importlib.util.spec_from_file_location("ot_art", os.path.join(here, "art.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.ART


ART = _load_art()


def esc(s):
    return html.escape(str(s), quote=True)


def module_path(mod_id, path):
    """Map a profile path to (repo, folder)."""
    if path.startswith("../opentracker-fx/"):
        return "fx", path[len("../opentracker-fx/"):]
    return "synths", path


def load_profiles(pdir):
    images = []
    for variant, prof, label, blurb in IMAGES:
        with open(os.path.join(pdir, prof + ".toml"), "rb") as f:
            t = tomllib.load(f)
        if t.get("variant") != variant or t.get("name") != prof:
            sys.exit(f"{prof}.toml: expected variant {variant}")
        mods = []
        for m in t.get("modules", []):
            mid = m["id"]
            if mid not in MODULES:
                sys.exit(f"{prof}.toml: unknown module {mid}: add it to MODULES")
            repo, folder = module_path(mid, m["path"])
            info = MODULES[mid]
            if (repo, folder) != (info["repo"], info["folder"]):
                sys.exit(f"{prof}.toml: {mid} path {m['path']} does not match {info['repo']}/{info['folder']}")
            mods.append(mid)
        images.append(dict(variant=variant, profile=prof, name=label, blurb=blurb,
                           file=f"PolyendTrackerOT{variant}300.ptf",
                           patches=f"Patches-{prof}-3.0.0.zip", modules=mods))
    return images


def read_sums(adir, tag):
    p = os.path.join(adir, tag, "SHA256SUMS")
    rows = []
    with open(p) as f:
        for line in f:
            h, name = line.split(None, 1)
            name = name.strip().lstrip("*")
            rows.append((name, h, os.path.getsize(os.path.join(adir, tag, name))))
    rows.append(("SHA256SUMS", None, os.path.getsize(p)))
    return rows


def size_str(n):
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f} MB"
    if n >= 1000:
        return f"{n / 1000:.1f} KB"
    return f"{n} B"


def asset_table(tag, rows, images):
    by_file = {i["file"]: f"{i['name']} image" for i in images}
    by_file.update({i["patches"]: f"Patches for the {i['name']} image" for i in images})
    out = ['<div class="table-wrap"><table>',
           f'<caption>Assets of release <code>{esc(tag)}</code></caption>',
           '<thead><tr><th scope="col">File</th><th scope="col">What it is</th>'
           '<th scope="col">Size</th><th scope="col">SHA256</th></tr></thead><tbody>']
    for name, h, size in rows:
        what = ASSET_DESC.get(name) or by_file.get(name, "")
        if not what and name.endswith(".zip"):
            what = "Tester zip: the images, all their patches and the README in one file"
        out.append(
            f'<tr><th scope="row"><a href="{DL}/{esc(tag)}/{esc(name)}">{esc(name)}</a></th>'
            f'<td>{esc(what)}</td><td class="num">{size_str(size)}</td>'
            f'<td class="sha">{esc(h) if h else "&mdash;"}</td></tr>')
    out.append("</tbody></table></div>")
    return "\n".join(out)


def image_rows(images):
    out = []
    for im in sorted(images, key=lambda i: FEATURED.index(i["profile"])):
        syn = ", ".join(MODULES[m]["name"] for m in im["modules"] if MODULES[m]["kind"] == "synth")
        fx = ", ".join(MODULES[m]["name"] for m in im["modules"] if MODULES[m]["kind"] == "effect")
        out.append(
            f'<tr data-variant="{im["variant"]}" id="image-{im["profile"]}">'
            f'<th scope="row"><span class="key" aria-hidden="true">{im["variant"]}</span> {esc(im["name"])}</th>'
            f'<td data-label="File"><a href="{DL}/{PREVIEW_TAG}/{im["file"]}"><code>{im["file"]}</code></a></td>'
            f'<td data-label="Synths">{esc(syn)}</td>'
            f'<td data-label="Effects">{esc(fx)}</td>'
            f'<td data-label="For">{esc(im["blurb"])}</td>'
            f'<td data-label="Patches"><a href="{DL}/{PREVIEW_TAG}/{im["patches"]}">{im["patches"]}</a></td></tr>')
    return "\n".join(out)


def module_cards(images, kind):
    out = []
    for mid, m in MODULES.items():
        if m["kind"] != kind:
            continue
        ims = [i for i in images if mid in i["modules"]]
        if not ims:
            continue  # in no released image
        chips = "".join(
            f'<li><a href="images.html#get-{i["profile"]}"><span class="key small" aria-hidden="true">{i["variant"]}</span> {esc(i["name"])}</a></li>'
            for i in ims)
        if m["patches"] is None:
            patches = "none (an effect)"
        elif m["patches"] == 0:
            patches = "none yet: start from Init"
        else:
            patches = f'{m["patches"]} {"kits" if mid == "TTY1" else "patches"}'
        url = f'{REPO[m["repo"]]}/{m["folder"]}'
        repo_name = "opentracker-synths" if m["repo"] == "synths" else "opentracker-fx"
        source = f'\n    <dt>Source</dt><dd><a href="{url}">{repo_name}/{m["folder"]}</a></dd>' if PUBLIC_REPOS else ""
        tag = '<span class="tag fx">effect</span>' if kind == "effect" else '<span class="tag">synth</span>'
        out.append(f'''<article class="panel module" id="mod-{mid.lower()}">
  <div class="card-head"><h3>{esc(m["name"])}</h3>{tag}</div>
  <div class="sub">module id {mid}</div>
  <p>{esc(m["desc"])}</p>
  <dl class="meta">
    <dt>Images</dt><dd><ul class="chips">{chips}</ul></dd>
    <dt>Patches</dt><dd>{esc(patches)}</dd>{source}
  </dl>
</article>''')
    return "\n".join(out)


DL_ICON = ('<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" focusable="false">'
           '<path d="M12 3v12m0 0-5-5m5 5 5-5M4 19h16" fill="none" stroke="currentColor" stroke-width="2.4" '
           'stroke-linecap="round" stroke-linejoin="round"/></svg>')


def chip_list(mids, cls):
    return f'<ul class="chips {cls}">' + "".join(f"<li>{esc(MODULES[m]['name'])}</li>" for m in mids) + "</ul>"


def file_html(fname, variant=None):
    """The image name, with the flavour letter (position 16) marked so it stands out."""
    if variant and len(fname) == 24 and fname[16] == variant:
        return f'{fname[:16]}<b class="vchar">{variant}</b>{fname[17:]}'
    return fname


def dl_button(url, label, fname, size, extra_cls="", variant=None):
    return f'''<a class="dl-btn{extra_cls}" href="{url}">
      <span class="dl-top">{DL_ICON} {label}</span>
      <span class="dl-file">{file_html(fname, variant)}</span>
      <span class="dl-meta">{size_str(size)} &middot; copy to <code>/Firmware</code>, keep the name</span>
    </a>'''


def flavour_card(im, sizes, dates, compact=False, level=3):
    p, v = im["profile"], im["variant"]
    syn = [m for m in im["modules"] if MODULES[m]["kind"] == "synth"]
    fx = [m for m in im["modules"] if MODULES[m]["kind"] == "effect"]
    url = f"{DL}/{PREVIEW_TAG}/{im['file']}"
    purl = f"{DL}/{PREVIEW_TAG}/{im['patches']}"
    cls = "flav flav-" + p + (" flav-compact" if compact else "")
    hid = f"flav-{p}-h"
    src = (f' &middot;\n    <a href="{FW_REPO}/blob/3.x/reimpl/profiles/{p}.toml">source: profiles/{p}.toml</a>'
           if PUBLIC_REPOS else "")
    return f'''<article class="{cls}" id="get-{p}" data-variant="{v}" aria-labelledby="{hid}">
  <div class="flav-art">{ART[p]()}<span class="badge badge-preview">Preview 3.0.0</span></div>
  <div class="flav-body">
    <h{level} class="flav-name" id="{hid}"><span class="key flav-key" aria-hidden="true">{v}</span> {esc(im["name"])}</h{level}>
    <p class="flav-vibe">{esc(VIBE[p])}</p>
    <div class="flav-mods">
      <span class="mods-label">Synths</span>{chip_list(syn, "chips-syn")}
      <span class="mods-label">Effects</span>{chip_list(fx, "chips-fx")}
    </div>
    {dl_button(url, f"Download the {esc(im['name'])} image", im["file"], sizes[im["file"]], variant=v)}
    <a class="flav-patch" href="{purl}">Patches: <span class="mono">{im["patches"]}</span> ({size_str(sizes[im["patches"]])})</a>
    <p class="fw-meta"><span>{PREVIEW_VERSION}</span> &middot; <span>{dates.get(im["file"], "")}</span>{src}</p>
  </div>
</article>'''


def stable_card(sizes):
    v = STABLE_VERSION

    def f(n):
        return f"{DL}/{STABLE_TAG}/{n}"
    files = [
        (f"OpenTracker-{v}-Patches.zip", "Patches", "", "82 patches"),
        (f"OpenTracker-{v}-Themes.zip", "Themes", ' <span class="badge badge-new">New</span>', "12 colour themes"),
        (f"OpenTracker-{v}-Projects.zip", "Test songs", "", "copy to /Projects"),
        (f"OpenTracker-{v}-Manual.pdf", "Manual (PDF)", "", "the 2.x user manual"),
    ]
    src = f' &middot;\n    <a href="{FW_REPO}/tree/2.x">source: branch 2.x</a>' if PUBLIC_REPOS else ""
    lis = "".join(f'<li><a href="{f(n)}">{label}</a>{extra} <span class="meta">{what}, {size_str(sizes[n])}</span></li>'
                  for n, label, extra, what in files)
    return f'''<article class="stable" aria-labelledby="stable-h">
  <div class="stable-info">
    <p class="stable-badges"><span class="badge badge-stable">Stable</span> <span class="badge badge-ver">2.x line</span></p>
    <h3 id="stable-h">OpenTracker {v}</h3>
    <p>One image with all of the 2.x line: 16 tracks, five synth engines (ACD, FAT, VAP, WTFM, PERC),
    stereo samples, Mini-format projects, USB Storage mode, live resampling, streaming from the card and
    colour themes. <strong>Use this one for real work.</strong></p>
    <ul class="stable-files">{lis}</ul>
    <p class="btn-row"><a class="btn" href="{CONTRIBUTE}">Source on GitHub: fork it and contribute</a></p>
  </div>
  <div class="stable-dl">
    {dl_button(f(STABLE_IMAGE), f"Download OpenTracker {v}", STABLE_IMAGE, sizes[STABLE_IMAGE], " dl-stable")}
    <a class="flav-patch" href="downloads.html#{STABLE_TAG}">All files, checksums and release notes</a>
    <p class="fw-meta"><span>{v}</span> &middot; <span>{STABLE_DATE}</span>{src}</p>
  </div>
</article>'''


def flavour_sections(images):
    out = []
    for p in FEATURED:
        im = next(i for i in images if i["profile"] == p)
        feats = "".join(f'<div class="feat"><h4>{esc(h)}</h4><p>{esc(d)}</p></div>' for h, d in FEATURES[p])
        shots = "".join(
            f'<figure class="device"><div class="bezel"><div class="screen">'
            f'<a href="assets/shots/{f}" title="Open at full size (800 x 480)"><img src="assets/shots/{f}" width="800" height="480" alt="{esc(c)}" loading="lazy"></a></div>'
            f'<span class="bezel-led" aria-hidden="true"></span></div><figcaption>{esc(c)}</figcaption></figure>'
            for f, c in SHOTS.get(p, []))
        shots_div = f'\n  <div class="shots">{shots}</div>' if shots else ""
        out.append(f'''<section class="inside inside-{p}" id="inside-{p}" aria-labelledby="inside-{p}-h">
  <div class="inside-head">
    <span class="key flav-key" aria-hidden="true">{im["variant"]}</span>
    <h3 id="inside-{p}-h">Inside {esc(im["name"])}</h3>
    <p class="inside-tag">{esc(TAGLINE[p])}</p>
    <a class="btn" href="#get-{p}">Get <span class="mono">{im["file"]}</span></a>
  </div>
  <div class="feats">{feats}</div>{shots_div}
</section>''')
    return "\n".join(out)


def md_inline(s):
    s = esc(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', s)
    return s


def md_to_html(text, shift=1):
    """A tiny Markdown subset: headings, paragraphs, - lists, 1. lists, **bold**, `code`."""
    out, para, lst = [], [], None

    def flush_para():
        if para:
            out.append(f"<p>{md_inline(' '.join(para))}</p>")
            para.clear()

    def close_list():
        nonlocal lst
        if lst:
            out.append(f"</{lst}>")
            lst = None

    for line in text.splitlines():
        if not line.strip():
            flush_para()
            close_list()
            continue
        m = re.match(r"(#+)\s+(.*)", line)
        if m:
            flush_para(); close_list()
            lvl = min(len(m.group(1)) + shift, 6)
            out.append(f"<h{lvl}>{md_inline(m.group(2))}</h{lvl}>")
            continue
        m = re.match(r"(-|\d+\.)\s+(.*)", line)
        if m:
            flush_para()
            kind = "ul" if m.group(1) == "-" else "ol"
            if lst != kind:
                close_list()
                out.append(f"<{kind}>")
                lst = kind
            out.append(f"<li>{md_inline(m.group(2))}</li>")
            continue
        if lst and line.startswith("  "):
            out[-1] = out[-1][:-5] + " " + md_inline(line.strip()) + "</li>"
            continue
        close_list()
        para.append(line.strip())
    flush_para()
    close_list()
    return "\n".join(out)


def header(page):
    items = [("index.html", "Home"), ("images.html", "3.0 images"),
             ("modules.html", "Synths &amp; effects"), ("downloads.html", "Downloads")]
    nav = "".join(
        f'<li><a href="{href}"{" aria-current=\"page\"" if href == page else ""}>{label}</a></li>'
        for href, label in items)
    return f'''<a class="skip" href="#main">Skip to content</a>
<div class="topbar"><div class="wrap">
  <a href="index.html#flavours"><span class="badge badge-preview">3.0 preview</span> Techno &middot; IDM &middot; Classic &middot; Retro</a>
  <span class="topbar-sep" aria-hidden="true">|</span>
  <a href="index.html#stable"><span class="badge badge-stable">Stable</span> 2.2.3</a>
</div></div>
<header class="site-head">
  <div class="wrap">
    <a class="brand" href="index.html" aria-label="OpenTracker home">
      <svg width="28" height="28" viewBox="0 0 32 32" aria-hidden="true" focusable="false"><rect x="1" y="1" width="30" height="30" rx="6" fill="#15181b" stroke="#3d444c" stroke-width="2"/><rect x="6" y="7" width="4" height="4" rx="1" fill="#ffb22e"/><rect x="22" y="7" width="4" height="4" rx="1" fill="#36e0b8"/><rect x="14" y="14" width="4" height="4" rx="1" fill="#ffb22e"/><rect x="6" y="21" width="4" height="4" rx="1" fill="#36e0b8"/><rect x="22" y="21" width="4" height="4" rx="1" fill="#ffb22e"/></svg>
      <span class="brand-name">Open<b>Tracker</b></span>
    </a>
    <nav class="nav" aria-label="Main"><ul>{nav}</ul></nav>
  </div>
</header>'''


FOOTER_CODE = f'''
      <div>
        <h2>Code</h2>
        <ul>
          <li><a href="https://github.com/{ORG}/opentracker">opentracker</a>: the firmware</li>
          <li><a href="https://github.com/{ORG}/opentracker-synths">opentracker-synths</a>: synth modules</li>
          <li><a href="https://github.com/{ORG}/opentracker-fx">opentracker-fx</a>: effect modules</li>
        </ul>
      </div>''' if PUBLIC_REPOS else ""

FOOTER = f'''<footer class="site-foot">
  <div class="wrap">
    <div class="foot-grid">{FOOTER_CODE}
      <div>
        <h2>Help</h2>
        <ul>
          <li><a href="{ISSUES}">Report a bug or ask a question</a></li>
          <li><a href="index.html#install">How to install</a></li>
          <li><a href="downloads.html">All releases and checksums</a></li>
        </ul>
      </div>
      <div>
        <h2>Site</h2>
        <ul>
          <li><a href="images.html">Pick a 3.0 image</a></li>
          <li><a href="modules.html">Synths &amp; effects</a></li>
          <li><a href="https://github.com/{ORG}/{SITE_REPO}">Site source</a></li>
        </ul>
      </div>
    </div>
    <p class="disclaimer">OpenTracker is a community project. It is not affiliated with, endorsed by or supported by
    Polyend. &ldquo;Polyend&rdquo; and &ldquo;Tracker&rdquo; are names of their owner, used here only to say which
    hardware this firmware runs on.</p>
  </div>
</footer>'''


def replace_block(text, name, content, fname):
    pat = re.compile(rf"(<!-- GEN:{re.escape(name)} -->)(.*?)(<!-- /GEN:{re.escape(name)} -->)", re.S)
    if not pat.search(text):
        sys.exit(f"{fname}: marker GEN:{name} missing")
    return pat.sub(lambda m: m.group(1) + "\n" + content + "\n" + m.group(3), text)


def sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_sums(folder):
    """Verify a SHA256SUMS file in folder; exit on any mismatch."""
    with open(os.path.join(folder, "SHA256SUMS")) as f:
        for line in f:
            want, name = line.split(None, 1)
            name = name.strip().lstrip("*")
            if sha256(os.path.join(folder, name)) != want:
                sys.exit(f"{folder}/{name}: SHA256 does not match SHA256SUMS")


def stage_preview(releases, assets, tester_zip=None):
    """Copy the published 3.0 images and their patch zips into <assets>/<PREVIEW_TAG>/,
    renaming Patches.zip to Patches-<flavour>-3.0.0.zip, and write a fresh SHA256SUMS."""
    import shutil
    import zipfile
    dest = os.path.join(assets, PREVIEW_TAG)
    allowed = set()
    plan = []
    for variant, prof, _, _ in IMAGES:
        src = os.path.join(releases, f"3.0.0-{prof}")
        check_sums(src)
        ptf = f"PolyendTrackerOT{variant}300.ptf"
        allowed.add(ptf)
        plan += [(os.path.join(src, ptf), ptf),
                 (os.path.join(src, "Patches.zip"), f"Patches-{prof}-3.0.0.zip")]
    if tester_zip:
        with zipfile.ZipFile(tester_zip) as z:
            extra = {os.path.basename(n) for n in z.namelist() if n.endswith(".ptf")} - allowed
        if extra:
            sys.exit(f"{tester_zip} holds images that are not published: {', '.join(sorted(extra))}")
        plan.append((tester_zip, os.path.basename(tester_zip)))
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    for src, name in plan:
        shutil.copy2(src, os.path.join(dest, name))  # keeps the build date
    with open(os.path.join(dest, "SHA256SUMS"), "w") as f:
        for _, name in sorted(plan, key=lambda x: x[1]):
            f.write(f"{sha256(os.path.join(dest, name))}  {name}\n")
    check_sums(dest)
    print(f"staged {len(plan)} files in {dest}, SHA256SUMS checked")


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ap = argparse.ArgumentParser()
    ap.add_argument("--profiles", required=True)
    ap.add_argument("--assets", required=True)
    ap.add_argument("--stage-from", metavar="RELEASES",
                    help="first re-stage the 3.0 preview assets from RELEASES/3.0.0-<flavour>/")
    ap.add_argument("--tester-zip", metavar="ZIP", help="with --stage-from: also attach this tester zip")
    a = ap.parse_args()
    if a.stage_from:
        stage_preview(a.stage_from, a.assets, a.tester_zip)

    images = load_profiles(a.profiles)
    used = {m for i in images for m in i["modules"]}
    data = {
        "previewTag": PREVIEW_TAG,
        "images": images,
        "modules": [dict(id=k, name=v["name"], kind=v["kind"]) for k, v in MODULES.items() if k in used],
    }
    with open(os.path.join(root, "assets", "data.js"), "w") as f:
        f.write("/* Generated by tools/build.py from the firmware's reimpl/profiles/*.toml. Do not edit. */\n")
        f.write("window.OT_DATA = " + json.dumps(data, indent=2) + ";\n")

    notes = {}
    for tag in (STABLE_TAG, PREVIEW_TAG):
        with open(os.path.join(root, "notes", tag + ".md")) as f:
            notes[tag] = md_to_html(f.read(), shift=2)

    sums = {tag: read_sums(a.assets, tag) for tag in (STABLE_TAG, PREVIEW_TAG)}
    sizes = {n: s for rows in sums.values() for n, _, s in rows}
    by_p = {i["profile"]: i for i in images}
    dates = {}
    for tag in (STABLE_TAG, PREVIEW_TAG):
        for n, _, _ in sums[tag]:
            st = os.stat(os.path.join(a.assets, tag, n))
            dates[n] = __import__("datetime").date.fromtimestamp(st.st_mtime).isoformat()
    blocks = {
        "flavour-hero": "\n".join(flavour_card(by_p[p], sizes, dates) for p in FEATURED),
        "flavour-sections": flavour_sections(images),
        "stable-card": stable_card(sizes),
        "image-cards": "\n".join(flavour_card(by_p[p], sizes, dates, compact=True, level=2) for p in FEATURED),
        "image-rows": image_rows(images),
        "synth-cards": module_cards(images, "synth"),
        "effect-cards": module_cards(images, "effect"),
        f"assets-{STABLE_TAG}": asset_table(STABLE_TAG, sums[STABLE_TAG], images),
        f"assets-{PREVIEW_TAG}": asset_table(PREVIEW_TAG, sums[PREVIEW_TAG], images),
        f"notes-{STABLE_TAG}": notes[STABLE_TAG],
        f"notes-{PREVIEW_TAG}": notes[PREVIEW_TAG],
        "footer": FOOTER,
    }
    for page in ("index.html", "images.html", "modules.html", "downloads.html", "404.html"):
        p = os.path.join(root, page)
        with open(p) as f:
            text = f.read()
        text = replace_block(text, "header", header(page), page)
        for name, content in blocks.items():
            if f"<!-- GEN:{name} -->" in text:
                text = replace_block(text, name, content, page)
        with open(p, "w") as f:
            f.write(text)
    print("ok:", ", ".join(i["name"] for i in images))


if __name__ == "__main__":
    main()
