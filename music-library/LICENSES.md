# Music library licenses

No audio is committed to this repository. Each person imports their own downloads (see `README.md`), and
`.gitignore` keeps every audio file, `catalog.json` and copied license files out of git.

| Folder | Source | License | Status |
|---|---|---|---|
| `background/open-lofi/` | Open Lo-Fi | not shipped with the download | **UNVERIFIED.** The files carry a `made with suno` tag and no license file. Check the Open Lo-Fi terms (and Suno's terms for generated music) before publishing a video. Never redistribute the files. |
| `jingles/kenney/` | Kenney Music Jingles, [kenney.nl](https://kenney.nl) | CC0 1.0 (public domain) | Verified from the `License.txt` in the download (copied to `jingles/kenney/SOURCE_LICENSE.txt` on import). Credit to Kenney is welcome but not required. |

`catalog.json` stores the source and license of every analysed file, and each `music_plan.md` repeats them for
the track it chose, so the license is visible before a video goes out.

When you add another library, add a row here and an entry to `SOURCES` in `scripts/music.py`.
