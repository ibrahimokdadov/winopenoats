"""
Generate a demo GIF of WinOpenOats with dummy data.
Renders synthetic UI frames using Pillow.
"""
from PIL import Image, ImageDraw, ImageFont
import math, os

# ── Palette ──────────────────────────────────────────────────────────────────
BG         = (247, 246, 243)
SURFACE    = (255, 255, 255)
BORDER     = (226, 221, 214)
ACCENT     = ( 13, 148, 136)
ACCENT2    = ( 16, 185, 129)
TEXT       = ( 28,  26,  23)
TEXT_MUTED = (197, 189, 179)
TEXT_SUB   = (139, 126, 114)
YOU_C      = ( 15, 118, 110)
THEM_C     = (124,  58, 237)
RED        = (220,  38,  38)
RED_BG     = (255, 245, 245)
RED_BORDER = (252, 165, 165)
TEAL_BG    = (240, 253, 250)
TEAL_BD    = (153, 246, 228)
SUCCESS_BG = (240, 253, 244)
SUCCESS_BD = (187, 247, 208)
SUCCESS_C  = (  6,  95,  70)
SUGG_BG    = (255, 255, 255)
SUGG_BD    = (237, 232, 225)
HEADER_BG  = (242, 240, 236)

W, H = 480, 660

# ── Fonts ────────────────────────────────────────────────────────────────────
FONT_DIR = "C:/Windows/Fonts/"
def font(name, size):
    for f in [name, "segoeui.ttf", "arial.ttf"]:
        try:
            return ImageFont.truetype(FONT_DIR + f, size)
        except Exception:
            pass
    return ImageFont.load_default()

F_TITLE   = font("segoeuib.ttf",  14)
F_SECTION = font("segoeuib.ttf",   8)
F_BODY    = font("segoeui.ttf",   12)
F_SMALL   = font("segoeui.ttf",   10)
F_MONO    = font("consola.ttf",   11)
F_BTN     = font("segoeuib.ttf",  12)
F_SUGG    = font("segoeuib.ttf",  12)
F_COACH   = font("segoeui.ttf",   11)
F_BADGE   = font("segoeuib.ttf",   8)

# ── Helpers ───────────────────────────────────────────────────────────────────
def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rounded_rect(draw, xy, radius, fill, outline=None, width=1):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill,
                            outline=outline, width=width)

def text_w(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0]

def wrap_text(draw, text, font, max_w):
    words = text.split()
    lines, line = [], ""
    for w in words:
        test = (line + " " + w).strip()
        if text_w(draw, test, font) <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines

def pill_btn(draw, x, y, w, h, label, font, bg, fg, border, radius=14):
    rounded_rect(draw, [x, y, x+w, y+h], radius, bg, border, width=1)
    lw = text_w(draw, label, font)
    draw.text((x + (w-lw)//2, y + (h-12)//2), label, font=font, fill=fg)

# ── Accent strip ─────────────────────────────────────────────────────────────
def draw_accent(draw):
    # gradient teal → emerald via horizontal blend
    for px in range(W):
        t = px / W
        r = int(15  + t * (16  - 15))
        g = int(118 + t * (185 - 118))
        b = int(110 + t * (129 - 110))
        draw.line([(px, 0), (px, 2)], fill=(r, g, b))

# ── Header ────────────────────────────────────────────────────────────────────
def draw_header(draw, kb_chunks=0):
    draw.text((24, 16), "WinOpenOats", font=F_TITLE, fill=TEXT)
    kb = f"KB: {kb_chunks} chunks" if kb_chunks else ""
    if kb:
        kw = text_w(draw, kb, F_SMALL)
        draw.text((W - 24 - 28 - 8 - kw, 19), kb, font=F_SMALL, fill=TEXT_MUTED)
    # ⚙ button
    rounded_rect(draw, [W-24-26, 12, W-24, 12+26], 6, BG, None)
    draw.text((W-24-19, 14), "⚙", font=font("seguisym.ttf", 14), fill=TEXT_MUTED)

# ── Section header ────────────────────────────────────────────────────────────
def draw_section(draw, y, label):
    draw.text((24, y), label, font=F_SECTION, fill=TEXT_MUTED)

# ── Suggestion card ───────────────────────────────────────────────────────────
def draw_suggestion(draw, y, headline, coaching, source=None):
    x1, x2 = 24, W-24
    card_h = 52 + (16 if coaching else 0) + (14 if source else 0)
    # shadow
    rounded_rect(draw, [x1+2, y+2, x2+2, y+card_h+2], 8, (230,225,218))
    # card
    rounded_rect(draw, [x1, y, x2, y+card_h], 8, SUGG_BG, SUGG_BD)
    # left accent
    draw.rounded_rectangle([x1, y, x1+3, y+card_h], radius=8, fill=ACCENT)
    draw.rectangle([x1+3, y, x1+6, y+card_h], fill=ACCENT)  # square off right side of left accent

    # headline
    lines = wrap_text(draw, headline, F_SUGG, x2 - x1 - 28)
    ty = y + 12
    for ln in lines[:2]:
        draw.text((x1+14, ty), ln, font=F_SUGG, fill=TEXT)
        ty += 16

    # coaching
    if coaching:
        clines = wrap_text(draw, coaching, F_COACH, x2 - x1 - 28)
        for ln in clines[:1]:
            draw.text((x1+14, ty), ln, font=F_COACH, fill=TEXT_SUB)
        ty += 14

    # source + feedback buttons
    by = y + card_h - 20
    if source:
        draw.text((x1+14, by), f"📄 {source}", font=F_SMALL, fill=TEXT_MUTED)
    for i, (emoji, cx) in enumerate([("+", x2-52), ("−", x2-28)]):
        rounded_rect(draw, [cx, by-1, cx+20, by+17], 4, SURFACE, BORDER)
        draw.text((cx+4, by+1), emoji, font=F_SMALL, fill=TEXT_MUTED)

    return y + card_h + 8

# ── Empty suggestion placeholder ──────────────────────────────────────────────
def draw_sugg_empty(draw, y):
    msg = "Suggestions from your knowledge base will appear here"
    mw = text_w(draw, msg, F_SMALL)
    draw.text(((W - mw)//2, y), msg, font=F_SMALL, fill=TEXT_MUTED)
    return y + 20

# ── Transcript row ────────────────────────────────────────────────────────────
def draw_utt(draw, y, speaker, text, ts=""):
    color = YOU_C if speaker == "you" else THEM_C
    tag   = "YOU" if speaker == "you" else "THEM"
    # tag badge
    draw.text((24, y+2), tag, font=F_BADGE, fill=color)
    tw = text_w(draw, tag, F_BADGE)
    # dot separator
    draw.text((24+tw+4, y+1), "·", font=F_SMALL, fill=BORDER)
    # text
    lines = wrap_text(draw, text, F_MONO, W - 24 - 24 - 50)
    for i, ln in enumerate(lines):
        draw.text((24+tw+14, y + i*14), ln, font=F_MONO, fill=TEXT)
    # timestamp
    if ts:
        draw.text((W-24-30, y+1), ts, font=F_SMALL, fill=TEXT_MUTED)
    return y + max(len(lines), 1)*14 + 8

# ── Search bar ────────────────────────────────────────────────────────────────
def draw_search(draw, y, query=""):
    rounded_rect(draw, [24, y, W-24, y+30], 8, SURFACE, BORDER)
    ph = query if query else "Search transcript…"
    col = TEXT if query else TEXT_MUTED
    draw.text((36, y+9), ph, font=F_BODY, fill=col)
    return y + 38

# ── Divider ───────────────────────────────────────────────────────────────────
def draw_div(draw, y):
    draw.line([(0, y), (W, y)], fill=BORDER)

# ── Record / Stop button ──────────────────────────────────────────────────────
def draw_record_btn(draw, recording=False):
    bx, by, bw, bh = 24, H-58, 130, 38
    if recording:
        rounded_rect(draw, [bx, by, bx+bw, by+bh], 20, RED_BG, RED_BORDER, width=2)
        draw.text((bx+28, by+12), "⏹  Stop", font=F_BTN, fill=RED)
    else:
        rounded_rect(draw, [bx, by, bx+bw, by+bh], 20, SURFACE, BORDER, width=2)
        draw.text((bx+22, by+12), "⏺  Record", font=F_BTN, fill=TEXT_SUB)

def draw_notes_btn(draw):
    bx, by, bw, bh = 166, H-58, 72, 38
    rounded_rect(draw, [bx, by, bx+bw, by+bh], 6, BG, BORDER)
    draw.text((bx+18, by+12), "Notes", font=F_BTN, fill=TEXT_SUB)

def draw_levels(draw, mic_level=0.0, sys_level=0.0):
    def bar(rms, color):
        filled = int(min(rms * 5, 5))
        return filled, color
    yb = H - 44
    # YOU
    draw.text((W-180, yb), "YOU", font=F_BADGE, fill=YOU_C)
    for i in range(5):
        c = YOU_C if i < int(mic_level * 5) else BORDER
        draw.rectangle([W-158+i*8, yb, W-153+i*8, yb+8], fill=c)
    # THEM
    draw.text((W-100, yb), "THEM", font=F_BADGE, fill=THEM_C)
    for i in range(5):
        c = THEM_C if i < int(sys_level * 5) else BORDER
        draw.rectangle([W-74+i*8, yb, W-69+i*8, yb+8], fill=c)

# ── Toast ─────────────────────────────────────────────────────────────────────
def draw_toast(draw, message, level="success"):
    if level == "success":
        bg, bd, fg = SUCCESS_BG, SUCCESS_BD, SUCCESS_C
        lc = (16, 185, 129)
    else:
        bg, bd, fg = TEAL_BG, TEAL_BD, (15, 118, 110)
        lc = ACCENT
    tw = min(380, W - 48)
    tx = (W - tw) // 2
    ty = H - 80
    rounded_rect(draw, [tx, ty, tx+tw, ty+44], 6, bg, bd)
    draw.rectangle([tx, ty+6, tx+3, ty+44-6], fill=lc)
    draw.text((tx+16, ty+14), message, font=F_BODY, fill=fg)

# ── Full frame renderer ───────────────────────────────────────────────────────
def make_frame(
    recording=False,
    utterances=None,       # list of (speaker, text, ts)
    suggestions=None,      # list of (headline, coaching, source)
    show_toast=False,
    toast_msg="",
    toast_level="success",
    mic_level=0.0,
    sys_level=0.0,
    kb_chunks=0,
):
    utterances  = utterances  or []
    suggestions = suggestions or []

    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Accent strip
    draw_accent(draw)

    # Header
    draw_header(draw, kb_chunks)
    draw_div(draw, 50)

    y = 58

    # Suggestions
    draw_section(draw, y, "SUGGESTIONS")
    y += 16
    if suggestions:
        for s in suggestions[-1:]:   # show latest
            y = draw_suggestion(draw, y, *s)
    else:
        y = draw_sugg_empty(draw, y)
    y += 4

    # System audio banner (hidden when recording works fine)
    y += 2

    # Search
    y = draw_search(draw, y)

    # Transcript header
    draw_section(draw, y, "TRANSCRIPT")
    y += 16

    # Transcript scroll area background
    scroll_top = y
    scroll_bot = H - 70
    draw.rectangle([0, scroll_top, W, scroll_bot], fill=BG)

    if not utterances:
        msg = "Transcript will appear here once you start recording"
        mw = text_w(draw, msg, F_BODY)
        draw.text(((W-mw)//2, scroll_top + 40), msg, font=F_BODY, fill=TEXT_MUTED)
    else:
        ty = scroll_top + 4
        # show last N rows that fit
        visible = []
        temp_y = ty
        for utt in utterances:
            lines = wrap_text(draw, utt[1], F_MONO, W - 24 - 24 - 50)
            row_h = max(len(lines), 1)*14 + 8
            visible.append((utt, row_h))
        # trim to fit
        total = sum(r[1] for r in visible)
        while total > (scroll_bot - scroll_top - 8) and visible:
            total -= visible[0][1]
            visible.pop(0)
        for utt, _ in visible:
            ty = draw_utt(draw, ty, utt[0], utt[1], utt[2])

    # Divider
    draw_div(draw, scroll_bot)

    # Controls
    draw_record_btn(draw, recording)
    draw_notes_btn(draw)
    draw_levels(draw, mic_level, sys_level)

    # Toast overlay
    if show_toast:
        draw_toast(draw, toast_msg, toast_level)

    return img


# ── Script ────────────────────────────────────────────────────────────────────
DUMMY_TRANSCRIPT = [
    ("you",  "Hey, can you walk me through the Q1 roadmap?", "09:01"),
    ("them", "Sure! We're shipping the new onboarding flow in week two.", "09:01"),
    ("you",  "What about the API rate limiting work?", "09:02"),
    ("them", "That's pushed to Q2 — we need more load testing first.", "09:02"),
    ("you",  "Makes sense. Who owns the dashboard redesign?", "09:03"),
    ("them", "Sarah's leading it. She's targeting end of March.", "09:03"),
    ("you",  "Great. Let's make sure it's on the sprint board.", "09:04"),
    ("them", "Already added. We also need to revisit the caching strategy.", "09:04"),
]

DUMMY_SUGGESTIONS = [
    (
        "Rate limiting: use token bucket algorithm",
        "From your notes on scalable API design.",
        "api_design.md",
    ),
    (
        "Dashboard redesign — check Figma spec v3",
        "Mentioned in last week's design review notes.",
        "design_review.md",
    ),
]

def build_frames():
    frames = []
    durations = []

    def add(img, ms):
        frames.append(img)
        durations.append(ms)

    # 1. Idle state
    for _ in range(4):
        add(make_frame(), 500)

    # 2. Click record — button switches
    add(make_frame(recording=True), 400)
    add(make_frame(recording=True), 600)

    # 3. Transcript fills in one by one
    utts = []
    for i, utt in enumerate(DUMMY_TRANSCRIPT):
        utts.append(utt)
        mic  = 0.4 + 0.3 * math.sin(i * 1.3) if utt[0] == "you"  else 0.1
        sys  = 0.4 + 0.3 * math.sin(i * 1.1) if utt[0] == "them" else 0.1
        sugg = DUMMY_SUGGESTIONS[:1] if i >= 3 else []
        add(make_frame(recording=True, utterances=utts, suggestions=sugg,
                       mic_level=mic, sys_level=sys, kb_chunks=47), 900)
        # brief "speaking" animation
        add(make_frame(recording=True, utterances=utts, suggestions=sugg,
                       mic_level=mic*0.6, sys_level=sys*0.6, kb_chunks=47), 300)

    # 4. Second suggestion card appears
    utts_full = list(DUMMY_TRANSCRIPT)
    for _ in range(3):
        add(make_frame(recording=True, utterances=utts_full,
                       suggestions=DUMMY_SUGGESTIONS, kb_chunks=47,
                       mic_level=0.2, sys_level=0.15), 500)

    # 5. Stop recording
    add(make_frame(recording=False, utterances=utts_full,
                   suggestions=DUMMY_SUGGESTIONS, kb_chunks=47), 600)

    # 6. Toast: session saved
    for _ in range(5):
        add(make_frame(recording=False, utterances=utts_full,
                       suggestions=DUMMY_SUGGESTIONS, kb_chunks=47,
                       show_toast=True,
                       toast_msg="Session saved — 8 utterances",
                       toast_level="success"), 600)

    # 7. Toast fades, back to idle
    for _ in range(3):
        add(make_frame(recording=False, utterances=utts_full,
                       suggestions=DUMMY_SUGGESTIONS, kb_chunks=47), 500)

    return frames, durations


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "demo.gif")
    print("Rendering frames…")
    frames, durations = build_frames()
    print(f"  {len(frames)} frames")

    # Quantise each frame to 128 colours to keep GIF small
    palettised = []
    for f in frames:
        palettised.append(f.quantize(colors=128, method=Image.Quantize.MEDIANCUT))

    print("Saving GIF…")
    palettised[0].save(
        out,
        save_all=True,
        append_images=palettised[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )
    size_mb = os.path.getsize(out) / 1_000_000
    print(f"Done → {out}  ({size_mb:.2f} MB)")
    if size_mb > 10:
        print("WARNING: over 10 MB — re-running with fewer colors…")
