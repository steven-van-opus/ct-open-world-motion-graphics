"""Render four editable graphics for a fictional waterfront district."""

import argparse
import json
from functools import lru_cache
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
FPS = 30
FRAMES = 90
INK = '#081720'
PANEL = '#102a37'
TIDE = '#56efd8'
SUN = '#ffc06d'
PAPER = '#f2f5e9'
MUTED = '#b7cfd0'


@lru_cache(maxsize=None)
def font(size):
    for name in ('DejaVuSans-Bold.ttf', '/System/Library/Fonts/Supplemental/Arial Bold.ttf', 'arialbd.ttf'):
        try:
            return ImageFont.truetype(name, int(size))
        except OSError:
            continue
    return ImageFont.load_default(size=int(size))


def label(draw, point, words, size, color=PAPER, max_width=810, anchor='la'):
    face = font(size)
    while draw.textlength(words, font=face) > max_width and size > 12:
        size -= 2
        face = font(size)
    draw.text(point, words, font=face, fill=color, anchor=anchor)


def enter(seconds, offset=0, duration=.36):
    progress = min(1., max(0., (seconds - offset) / duration))
    return 1 - (1 - progress) ** 3


def chapter(draw, data, seconds):
    x = round(72 - 140 * (1 - enter(seconds)))
    draw.rounded_rectangle((x, 44, x + 902, 311), radius=26, fill=PANEL)
    draw.rounded_rectangle((x, 44, x + 902, 311), radius=26, outline=TIDE, width=2)
    draw.rectangle((x + 26, 81, x + 38, 273), fill=TIDE)
    label(draw, (x + 64, 80), data['eyebrow'], 28, TIDE, max_width=760)
    label(draw, (x + 64, 132), data['title'], 74, max_width=790)
    label(draw, (x + 66, 247), data['subtitle'], 25, MUTED, max_width=770)
    for index in range(4):
        start = x + 736 + index * 30
        draw.line((start, 110, start + 18, 79), fill=SUN, width=4)


def tier(draw, data, seconds):
    label(draw, (104, 31), 'ROUTE RANKING', 25, TIDE)
    label(draw, (100, 70), data['title'], 59)
    for index, ((grade, name), color) in enumerate(zip(data['ranks'], (SUN, TIDE, MUTED))):
        progress = enter(seconds, .1 + index * .18)
        if not progress:
            continue
        x = round(100 + 90 * (1 - progress))
        y = 155 + index * 62
        draw.rounded_rectangle((x, y, x + 880, y + 50), radius=11, fill=PANEL)
        draw.rounded_rectangle((x, y, x + 74, y + 50), radius=11, fill=color)
        label(draw, (x + 37, y + 25), grade, 28, INK, max_width=62, anchor='mm')
        label(draw, (x + 101, y + 9), name, 29, max_width=700)
        draw.line((x + 846, y + 25, x + 862, y + 25), fill=color, width=3)


def map_callout(draw, data, seconds):
    draw.rounded_rectangle((89, 34, 991, 326), radius=24, fill=PANEL)
    draw.rounded_rectangle((110, 56, 594, 304), radius=13, fill=INK)
    for x in range(134, 583, 24):
        draw.line((x, 66, x, 294), fill='#173542', width=1)
    for y in range(76, 295, 24):
        draw.line((120, y, 584, y), fill='#173542', width=1)
    shoreline = [(118, 230), (216, 230), (255, 270), (304, 270), (304, 228),
                 (343, 228), (375, 196), (441, 196), (487, 154), (581, 154)]
    draw.polygon(shoreline + [(581, 294), (120, 294)], fill='#153e52')
    draw.line(shoreline, fill='#4d8796', width=3, joint='curve')
    for road in [[(124, 104), (276, 104), (308, 135), (581, 135)],
                 [(125, 164), (232, 164), (273, 121), (273, 70)],
                 [(175, 70), (175, 195), (207, 227)],
                 [(335, 70), (335, 132), (311, 166), (311, 222)],
                 [(130, 207), (252, 207), (288, 171), (459, 171), (522, 110), (580, 110)],
                 [(467, 71), (467, 117), (430, 154), (430, 196)]]:
        draw.line(road, fill='#54818a', width=4, joint='curve')
    x, y = 426, 172
    reveal = enter(seconds, .18)
    ring = round(14 + 18 * reveal)
    draw.ellipse((x - ring, y - ring, x + ring, y + ring), outline=TIDE, width=2)
    draw.ellipse((x - 9, y - 9, x + 9, y + 9), fill=SUN)
    if reveal:
        draw.line((x + 23, y - 23, x + 70, y - 70), fill=TIDE, width=3)
        draw.line((x + 70, y - 70, 620, y - 70), fill=TIDE, width=3)
        label(draw, (631, 85), 'WAYPOINT', 24, TIDE, max_width=325)
        label(draw, (627, 134), data['title'], 62, max_width=330)
        label(draw, (630, 234), data['subtitle'], 20, MUTED, max_width=326)


def caption(draw, data, seconds):
    before_y = round(105 + 35 * (1 - enter(seconds)))
    accent_y = round(105 + 36 * (1 - enter(seconds, .26, .24)))
    lower_y = round(209 + 32 * (1 - enter(seconds, .62)))
    draw.rounded_rectangle((89, 69, 991, 298), radius=24, fill=INK)
    draw.line((119, 101, 119, 264), fill=TIDE, width=6)
    label(draw, (158, before_y), data['before'], 65, max_width=465)
    if seconds >= .26:
        draw.rounded_rectangle((645, accent_y, 938, accent_y + 74), radius=10, fill=SUN)
        label(draw, (791, accent_y + 37), data['accent'], 55, INK, max_width=265, anchor='mm')
    if seconds >= .62:
        label(draw, (158, lower_y), data['after'], 53, TIDE, max_width=765)


SCENES = {'chapter': chapter, 'tier': tier, 'map': map_callout, 'caption': caption}
SIZES = {'wide': (1920, 1080), 'vertical': (1080, 1920)}


@lru_cache(maxsize=2)
def background(size):
    width, height = size
    image = Image.new('RGBA', size, INK)
    draw = ImageDraw.Draw(image)
    for y in range(height):
        fraction = y / height
        draw.line((0, y, width, y), fill=(9 + int(12 * fraction), 24 + int(29 * fraction), 34 + int(32 * fraction)))
    for x in range(-height, width, 64):
        draw.line((x, 0, x + height, height), fill='#1c3d4b', width=1)
    draw.line((45, 72, width - 45, 72), fill='#3b6270', width=2)
    label(draw, (48, 31), 'HARBOR WARD  /  FIELD NOTES', 19, MUTED, max_width=width - 100)
    return image


def artwork(name, data, seconds):
    panel = Image.new('RGBA', (1080, 360))
    SCENES[name](ImageDraw.Draw(panel), data[name], seconds)
    fade = min(1., seconds / .16, max(0., (3 - seconds) / .22))
    if fade < 1:
        panel.putalpha(panel.getchannel('A').point(lambda value: int(value * fade)))
    return panel


def frame(name, data, seconds, size, transparent):
    width, height = size
    image = Image.new('RGBA', size) if transparent else background(size).copy()
    panel = artwork(name, data, seconds)
    if width < height:
        y = int(height * {'chapter': .31, 'tier': .37, 'map': .40, 'caption': .54}[name])
        image.alpha_composite(panel, (0, y))
    else:
        x = 115 if name == 'map' else (width - panel.width) // 2
        y = int(height * {'chapter': .31, 'tier': .33, 'map': .58, 'caption': .64}[name])
        image.alpha_composite(panel, (x, y))
    return image


def render(name, data, size, transparent, output):
    width, height = size
    codec = ['-c:v', 'prores_ks', '-profile:v', '4', '-pix_fmt', 'yuva444p10le'] if transparent else [
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-movflags', '+faststart'
    ]
    command = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'rawvideo',
               '-pix_fmt', 'rgba', '-s', f'{width}x{height}', '-r', str(FPS), '-i', '-', *codec, str(output)]
    with subprocess.Popen(command, stdin=subprocess.PIPE) as encoder:
        try:
            for index in range(FRAMES):
                encoder.stdin.write(frame(name, data, index / FPS, size, transparent).tobytes())
        except BrokenPipeError:
            pass
        finally:
            encoder.stdin.close()
        if encoder.wait() != 0:
            raise SystemExit(f'FFmpeg could not render {output}. Check the encoder error above.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scene', choices=(*SCENES, 'all'))
    parser.add_argument('--format', choices=SIZES, default='wide')
    parser.add_argument('--alpha', action='store_true', help='Export ProRes 4444 MOV with transparency.')
    parser.add_argument('--config', type=Path, default=ROOT / 'scenes.json')
    parser.add_argument('--out', type=Path, default=ROOT / 'renders')
    args = parser.parse_args()
    data = json.loads(args.config.read_text(encoding='utf-8'))
    args.out.mkdir(parents=True, exist_ok=True)
    for name in SCENES if args.scene == 'all' else (args.scene,):
        suffix = 'mov' if args.alpha else 'mp4'
        output = args.out / f'{name}-{args.format}.{suffix}'
        render(name, data, SIZES[args.format], args.alpha, output)
        print(output)


if __name__ == '__main__':
    main()
