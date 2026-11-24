# Creators Toolbox Open World Motion Graphics

Four animated graphics for video edits, set in the fictional waterfront district of Harbor Ward. Each scene lasts three seconds at 30 fps. The sample copy and map are original, and the renderer uses no gameplay footage, game logos or publisher files.

| Scene | What it does |
| --- | --- |
| `chapter` | Slides in a chapter number, title and subtitle. |
| `tier` | Reveals three ranked routes in order. |
| `map` | Highlights a fictional waypoint with a ring and callout. |
| `caption` | Pops in an emphasized phrase and follows it with a second line. |

[Creators Toolbox guide](https://creatorstoolbox.com/@steven/post/g_open-world-motion-graphics)

## Run the examples

Install Python 3.10 or newer and put FFmpeg on your PATH. The renderer needs an FFmpeg build with `libx264` for MP4 and `prores_ks` for transparency.

```sh
git clone https://github.com/steven-van-opus/ct-open-world-motion-graphics.git
cd ct-open-world-motion-graphics
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python render.py all --format wide
.venv/bin/python render.py caption --format vertical --alpha
```

On Windows, use `py -m venv .venv` and `.venv\Scripts\python.exe` in place of `.venv/bin/python`.

The default `renders/` directory gets four 1920 × 1080 MP4s and one 1080 × 1920 ProRes 4444 MOV. Use the MP4s as standalone cuts. Place the MOV one track above your footage in an editor that supports ProRes 4444 and alpha. Exports are silent. Keep a copy of the project files if you want to change the text later.

## Customize it with Claude Code

Run `claude` from the repo directory if you have Claude Code installed. Give it a specific edit and a single render to check.

> Read `scenes.json` and `render.py`. Make a copy of `scenes.json` called `my-edit.json`. Change the map title to Dock 12 and the subtitle to NORTH PIER / PICKUP. Keep the Harbor Ward map coordinates. Render `map` at 1080 × 1920 using `--config my-edit.json --format vertical --alpha`, then show me the output path.

You can edit the JSON and run the same render commands directly. Keep the tier array to three pairs and the caption's three phrases short so they stay readable. Change the map pin coordinates inside `map_callout()` if your new text needs a different spot. If you move the pin, review the line linking it to the label.

This independent Creators Toolbox project is unaffiliated with Rockstar Games and Grand Theft Auto.
