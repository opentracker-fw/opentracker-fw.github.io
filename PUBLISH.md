# Publishing OpenTracker under `opentracker-fw`

**This file is kept out of git on purpose** (it is listed in `.git/info/exclude`): it names private folders and the trademark grep, and anything committed here is served by Pages. Keep it local.

Run these steps in order. Nothing here has been pushed yet: every repository below exists only
on this machine. Read the **Check first** list before step 3.

| Repository | Local source | Branches to push |
|---|---|---|
| `opentracker-fw/opentracker-fw.github.io` | `~/Projects/opentracker-fw.github.io` | `main` |
| `opentracker-fw/opentracker-synths` | `~/Projects/opentracker-synths` | local `master` pushed as `main` |
| `opentracker-fw/opentracker-fx` | `~/Projects/opentracker-fx` | local `master` pushed as `main` |
| `opentracker-fw/opentracker` | a filtered export of `/home/sand/Projects/ReversedPolytracker` | `2.x`, `3.x` |

Release assets are staged outside the site repository, in
`~/Projects/opentracker-fw.github.io-assets/<tag>/`, each folder with its own `SHA256SUMS`.

## Check first: not safe to publish as it is

**Firmware repository.** `~/Projects/ReversedPolytracker-3x` is a git worktree of
`/home/sand/Projects/ReversedPolytracker` (branch `3.x`); `2.x` is checked out in the main
worktree. Both branches have no remote. Checked by name only
(`git ls-files | cut -d/ -f1 | sort -u` and the folder names below it):

- `analysis/`: on both branches and in the history of every branch. **Must not go public.**
- `reimpl/sim/fixtures/` and `reimpl/tests/fixtures/`: on both branches. **Must not go public.**
- `tools/` (`dump_decomp.py`, `rea-bridge/`, `carrier.S`, `carrier.ld`, `mkcarrier.sh`,
  `gen_seeds.py`): analysis helpers by their names. The `reimpl` build does not use them.
  Leave them out.
- `docs/specs/`, `docs/STRINGS_DIFF_1.9.3.md`, `docs/VISUAL_DIFF_1.9.4.md`,
  `docs/VERIFICATION_1TO1.md`, `docs/VERIFY_1.9.5.md`, `docs/verify_1.9.5/`,
  `docs/GAP_AUDIT.md`: comparisons with the stock firmware, by their names. The export
  below leaves them out; review them before you add any back.
- `reimpl/third_party/` (`fatfs`, `teensy3`, `fonts` with Roboto and Roboto Mono, `LICENSES`):
  vendor code with its own licence files. It can go public; keep the licence files.
- `reimpl/.github/workflows/ci.yml`: a workflow file. GitHub only runs workflows from the
  root `.github/`, so it does nothing there. Delete it if you want no workflow files at all.
- Product and trademark names in the text: `README.md`, `reimpl/README.md`, the
  `docs/RELEASE_NOTES_*` files, `reimpl/profiles/*.toml` comments ("Juno-style"), some
  `reimpl/tests` and `reimpl/src` files, and the line "clean-room" and the old download link
  in the READMEs. Fix them in the export before you push (the grep in step 4c lists them).

Because `analysis/` is in the history, **do not push the existing history**. Step 4 makes a
filtered export: one snapshot commit for `2.x` and one for `3.x` on top of it.

**opentracker-synths** (history: `.gitignore LICENSE Makefile modules README.md`, no
`analysis` or `fixtures`):

- `README.md` line 15 and `modules/ju6/src/ju6.cpp`, `ju6.h`, `tests/engine_ju6_test.cpp`
  name a trademark in comments ("Juno"). `modules/perc/src/perc.cpp` line 791 has a drum
  machine model number in a comment. Reword them.
- `modules/acd/src/acd.cpp` and `acd.h` say "clean-room" in their first lines.
- `README.md` links to `../ReversedPolytracker`; change it to
  `https://github.com/opentracker-fw/opentracker`.

**opentracker-fx** (history: `.gitignore LICENSE modules README.md`, no `analysis` or
`fixtures`):

- `modules/juno/` (module `JUNO`, "Juno chorus") has a trademark in its folder, module name,
  README row and source. It is in no released image (only the unreleased `full` profile).
  Rename it (for example `modules/ensemble`, module name "Ensemble chorus") and update
  `reimpl/profiles/full.toml`, or leave it out of the public repository.
- `README.md` links to `../ReversedPolytracker`; change it as above.

The old wording stays in the history of these two repositories. If that matters, publish a
fresh one-commit snapshot of each (as in step 4) instead of the history.

**Release assets.** Published scope: the 3.0 preview images Techno (`t`), IDM (`i`) and
Classic (`a`), and stable 2.2.3. Mini, No-FM and 2.2.2 are not published.

- `v2.2.3/OpenTracker-2.2.3-Manual.pdf` (fetched from the old release): its title page says
  "clean-room", mentions the licence and links to the old repository; inside it names
  products in the themes chapter (a fashion doll brand, a home computer, a handheld console)
  and the external gear of a bug report (two drum and synth products). Rebuild it with those
  pages reworded, then rerun the checksums (step 6a), or upload it as it is knowing that.
- `v2.2.3/OpenTracker-2.2.3-Themes.zip`: three theme files are named after trademarks
  (`Barbie.txt`, `C64.txt`, `GameBoy.txt`, and one file's text names the computer maker).
  Rename them (for example `Doll.txt`, `Breadbin.txt`, `Handheld.txt`) and rezip before
  upload, or upload it as it is knowing that. The site and notes don't name them.
- Patch names "OT Hoover Lead" and "OT Hoover Whoop" use the genre name for that sound; the
  2.2.3 test songs have sample names with "SID". Low risk.
- The patch folder names `JU6`, `DTYPE`, `CSTYPE`, `ATYPE`, `TTYPE` are the names the
  firmware uses on screen; they are left as they are.
- The old `OpenTracker-3.0.0-preview.zip` holds the Mini and No-FM images too, so it is not
  attached; `tools/build.py --tester-zip` refuses a zip with unpublished images.

## 1. Create the organisation (web)

Open <https://github.com/account/organizations/new>, choose the free plan and name it
`opentracker-fw`. Then check that the CLI can see it:

```
gh auth status
gh api orgs/opentracker-fw --jq .login
```

## 2. Create the four repositories

```
gh repo create opentracker-fw/opentracker-fw.github.io --public \
  --description "OpenTracker website and release downloads"
gh repo create opentracker-fw/opentracker --public \
  --description "OpenTracker: open, community firmware for the original Polyend Tracker"
gh repo create opentracker-fw/opentracker-synths --public \
  --description "Synth engine modules for OpenTracker 3"
gh repo create opentracker-fw/opentracker-fx --public \
  --description "Effect modules for OpenTracker 3"
```

## 3. Push the site repository

```
cd ~/Projects/opentracker-fw.github.io
git remote add origin git@github.com:opentracker-fw/opentracker-fw.github.io.git
git push -u origin main
```

## 4. Push the firmware as a filtered export

a. Make the export (about 80 MB of working files; the source is not changed):

```
SRC=/home/sand/Projects/ReversedPolytracker
EXP="$HOME/Projects/opentracker-export"
git init -b 2.x "$EXP"

export_branch () {
  git -C "$EXP" rm -rq --ignore-unmatch -- .
  git -C "$SRC" archive "$1" | tar -x -C "$EXP" \
    --exclude=analysis --exclude=fixtures \
    --anchored --exclude=tools --exclude=docs/specs --exclude=docs/verify_1.9.5 \
    --exclude=docs/STRINGS_DIFF_1.9.3.md --exclude=docs/VISUAL_DIFF_1.9.4.md \
    --exclude=docs/VERIFICATION_1TO1.md --exclude=docs/VERIFY_1.9.5.md \
    --exclude=docs/GAP_AUDIT.md
  git -C "$EXP" add -A
  git -C "$EXP" commit -qm "OpenTracker $1 ($(git -C "$SRC" rev-parse --short "$1"))"
}

export_branch 2.x
git -C "$EXP" switch -c 3.x
export_branch 3.x
```

`analysis` and `fixtures` are matched as folder names anywhere in the tree. After
`--anchored`, the other patterns match only from the top, so `tools` drops the top-level
`tools/` and keeps `reimpl/tools/` (the build needs it).

b. Check it. These must print nothing:

```
git -C "$EXP" ls-files | grep -E '(^|/)(analysis|fixtures)/'
git -C "$EXP" log --all --name-only --format= | grep -E '(^|/)(analysis|fixtures)/'
```

Then build and test it (`make -C "$EXP/reimpl"` on each branch). Tests that read fixtures will
be missing their data; turn them off or replace the data with files you made yourself.

c. Fix the names listed in **Check first**, commit on each branch, and grep again:

```
git -C "$EXP" grep -nEI 'Moog|Minimoog|Yamaha|CS-80|ARP |Odyssey|2600|Roland|Juno|TR-[0-9]|909|808|606|Prophet|Virus|clean-room|reverse.engineer|polyend-tracker-re'
```

d. Push:

```
cd "$EXP"
git remote add origin git@github.com:opentracker-fw/opentracker.git
git push -u origin 2.x
git push -u origin 3.x
gh repo edit opentracker-fw/opentracker --default-branch 2.x
```

Do not push the `opentracker` (1.9.x) branch or any of the `fix-*`, `pr*` and test branches.

## 5. Push the module repositories

After the fixes in **Check first**:

```
cd ~/Projects/opentracker-synths
git remote add origin git@github.com:opentracker-fw/opentracker-synths.git
git push -u origin master:main
gh repo edit opentracker-fw/opentracker-synths --default-branch main

cd ~/Projects/opentracker-fx
git remote add origin git@github.com:opentracker-fw/opentracker-fx.git
git push -u origin master:main
gh repo edit opentracker-fw/opentracker-fx --default-branch main
```

The site links to `.../tree/main/modules/<name>`, so the branch on GitHub must be `main`.
Optionally rename the local branches too: `git branch -m master main` and
`git branch -u origin/main`.

## 6. Create the releases on the site repository

a. Re-stage the 3.0 images after a rebuild (this checks each release folder's own
`SHA256SUMS`, copies the three images and their patch zips, writes and checks a new combined
`SHA256SUMS`, then regenerates the sizes, hashes and dates on the pages):

```
cd ~/Projects/opentracker-fw.github.io
python3 -I tools/build.py --profiles ~/Projects/ReversedPolytracker-3x/reimpl/profiles \
  --assets ~/Projects/opentracker-fw.github.io-assets \
  --stage-from /home/sand/Projects/ReversedPolytracker/releases
# add  --tester-zip /path/to/the-new-tester.zip  to attach the tester zip too
git add -A && git commit -m "Re-stage 3.0.0 preview assets"
```

Check both tags:

```
A="$HOME/Projects/opentracker-fw.github.io-assets"
(cd "$A/v2.2.3" && sha256sum -c SHA256SUMS)
(cd "$A/v3.0.0-preview" && sha256sum -c SHA256SUMS)
```

b. Create the releases:

```
cd ~/Projects/opentracker-fw.github.io
A="$HOME/Projects/opentracker-fw.github.io-assets"

gh release create v2.2.3 --repo opentracker-fw/opentracker-fw.github.io \
  --target main --title "OpenTracker 2.2.3" --notes-file notes/v2.2.3.md --latest \
  "$A"/v2.2.3/*

gh release create v3.0.0-preview --repo opentracker-fw/opentracker-fw.github.io \
  --target main --title "OpenTracker 3.0.0 preview" --notes-file notes/v3.0.0-preview.md \
  --prerelease "$A"/v3.0.0-preview/*
```

Assets: `v2.2.3` has `PolyendTrackerOTv223.ptf`, `OpenTracker-2.2.3-Patches.zip`,
`OpenTracker-2.2.3-Projects.zip`, `OpenTracker-2.2.3-Themes.zip`,
`OpenTracker-2.2.3-Manual.pdf` and `SHA256SUMS`. `v3.0.0-preview` has
`PolyendTrackerOT{a,i,t}300.ptf`, `Patches-{classic,idm,techno}-3.0.0.zip`, the tester zip if
you staged one, and `SHA256SUMS`.

## 7. Turn on GitHub Pages

In the web UI: **Settings > Pages > Build and deployment > Source: Deploy from a branch**,
branch `main`, folder `/ (root)`, Save. Or with the CLI:

```
gh api -X POST repos/opentracker-fw/opentracker-fw.github.io/pages \
  -f 'source[branch]=main' -f 'source[path]=/'
gh api repos/opentracker-fw/opentracker-fw.github.io/pages --jq '.html_url,.status'
```

The repository has a `.nojekyll` file, so Pages serves the files as they are. The site is at
<https://opentracker-fw.github.io/> after a minute or two. Then open every page and try one
download link from each release.
