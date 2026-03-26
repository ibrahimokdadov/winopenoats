"""
Generates demo_update.gif showing the new WinOpenOats features:
  - Meeting templates selector
  - Mic mute toggle
  - Transcript with longer flush (natural sentences)
  - Custom endpoint hint in settings
Run: python scripts/make_update_gif.py
Output: demo_update.gif (in repo root)
"""
from PIL import Image, ImageDraw, ImageFont
import os, sys

# ── Dimensions & palette ──────────────────────────────────────────
W, H = 480, 700
BG         = (247, 246, 243)
TEXT       = (28,  26,  23)
MUTED_TEXT = (197, 189, 179)
BORDER     = (226, 221, 214)
ACCENT     = (13,  148, 136)
YOU_CLR    = (15,  118, 110)
THEM_CLR   = (124, 58,  237)
REC_BG     = (255, 245, 245)
REC_BORDER = (252, 165, 165)
REC_TEXT   = (220, 38,  38)
MUTE_BG    = (254, 252, 232)
MUTE_BDR   = (253, 230, 138)
MUTE_TEXT  = (120, 53,  15)
CARD_BG    = (255, 255, 255)
TOAST_BG   = (240, 253, 250)
TOAST_BDR  = (153, 246, 228)
TOAST_ACC  = (13,  148, 136)
TOAST_TEXT = (15,  118, 110)
TEAL_GRAD  = [(15, 118, 110), (13, 148, 136), (16, 185, 129)]
WHITE      = (255, 255, 255)

# ── Font loader ───────────────────────────────────────────────────
FONT_DIR = "C:/Windows/Fonts/"

def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for f in [name, "segoeui.ttf", "segoeuil.ttf", "calibri.ttf", "arial.ttf"]:
        try:
            return ImageFont.truetype(FONT_DIR + f, size)
        except Exception:
            pass
    return ImageFont.load_default()

F_TITLE   = font("segoeuib.ttf", 15)
F_SECTION = font("segoeuib.ttf", 8)
F_BODY    = font("segoeui.ttf",  12)
F_MONO    = font("consola.ttf",  11)
F_SMALL   = font("segoeui.ttf",  10)
F_TAG     = font("segoeuib.ttf", 8)
F_BTN     = font("segoeui.ttf",  12)
F_BTN_REC = font("segoeuib.ttf", 13)
F_TOAST   = font("segoeui.ttf",  13)

def wrap(draw, text, font, max_w):
    words = text.split()
    lines, line = [], ""
    for w in words:
        test = (line + " " + w).strip()
        if draw.textlength(test, font=font) <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines

# ── Components ────────────────────────────────────────────────────

def draw_accent_strip(img):
    draw = ImageDraw.Draw(img)
    for x in range(W):
        t = x / W
        r = int(TEAL_GRAD[0][0] * (1-t) + TEAL_GRAD[2][0] * t)
        g = int(TEAL_GRAD[0][1] * (1-t) + TEAL_GRAD[2][1] * t)
        b = int(TEAL_GRAD[0][2] * (1-t) + TEAL_GRAD[2][2] * t)
        draw.line([(x, 0), (x, 2)], fill=(r, g, b))

def draw_header(draw, kb_text=""):
    draw.text((24, 16), "OpenOats", font=F_TITLE, fill=TEXT)
    if kb_text:
        w = draw.textlength(kb_text, font=F_SMALL)
        draw.text((W - 24 - 28 - 8 - w, 18), kb_text, font=F_SMALL, fill=MUTED_TEXT)
    # gear icon (circle + dot)
    cx, cy = W - 24 - 14, 22
    draw.ellipse([cx-11, cy-11, cx+11, cy+11], outline=MUTED_TEXT, width=1)
    draw.ellipse([cx-4, cy-4, cx+4, cy+4], outline=MUTED_TEXT, width=1)

def draw_section_label(draw, y, text):
    for i, ch in enumerate(text):
        x = 24 + i * 7
        draw.text((x, y), ch, font=F_SECTION, fill=MUTED_TEXT)

def draw_suggestion_card(draw, y, headline, coaching, source):
    draw.rounded_rectangle([24, y, W-24, y+72], radius=8,
                            fill=CARD_BG, outline=(13, 148, 136))
    draw.rectangle([24, y, 27, y+72], fill=ACCENT)
    draw.rounded_rectangle([24, y, 27, y+72], radius=0, fill=ACCENT)
    lines = wrap(draw, headline, F_BODY, W - 24 - 24 - 20)
    draw.text((38, y+10), lines[0] if lines else headline, font=F_BODY, fill=TEXT)
    draw.text((38, y+28), coaching[:55] + "…" if len(coaching) > 55 else coaching,
              font=F_SMALL, fill=MUTED_TEXT)
    draw.text((38, y+50), f"📄 {source}", font=F_SMALL, fill=MUTED_TEXT)

def draw_empty_suggestions(draw, y):
    draw.text((24, y), "Suggestions from your knowledge base will appear here",
              font=F_SMALL, fill=MUTED_TEXT)

def draw_search(draw, y, query=""):
    draw.rounded_rectangle([24, y, W-24, y+30], radius=8, fill=WHITE, outline=BORDER)
    placeholder = query if query else "Search transcript…"
    fill = TEXT if query else MUTED_TEXT
    draw.text((36, y+9), placeholder, font=F_BODY, fill=fill)

def draw_utterance(draw, y, speaker, text):
    color = YOU_CLR if speaker == "you" else THEM_CLR
    tag   = "YOU" if speaker == "you" else "THEM"
    draw.text((24, y), tag, font=F_TAG, fill=color)
    draw.text((55, y-1), "·", font=F_BODY, fill=MUTED_TEXT)
    lines = wrap(draw, text, F_MONO, W - 24 - 80)
    for i, ln in enumerate(lines[:2]):
        draw.text((66, y + i*16 - 1), ln, font=F_MONO, fill=TEXT)
    return 16 * min(len(lines), 2) + 10

def draw_empty_transcript(draw, y):
    msg = "Transcript will appear here once you start recording"
    w = draw.textlength(msg, font=F_SMALL)
    draw.text(((W - w) // 2, y + 30), msg, font=F_SMALL, fill=MUTED_TEXT)

def draw_separator(draw, y):
    draw.line([(24, y), (W-24, y)], fill=BORDER)

def draw_controls(draw, y, recording=False, muted=False, rec_label="⏺  Record"):
    # Record button (pill)
    if recording:
        rbg, rbdr, rtxt = REC_BG, REC_BORDER, REC_TEXT
    else:
        rbg, rbdr, rtxt = WHITE, BORDER, (107, 96, 89)
    draw.rounded_rectangle([24, y, 168, y+40], radius=20, fill=rbg, outline=rbdr, width=2)
    rw = draw.textlength(rec_label, font=F_BTN_REC)
    draw.text(((24 + 168 - rw) // 2, y + 12), rec_label, font=F_BTN_REC, fill=rtxt)

    # Mute button
    if muted:
        mbg, mbdr, mtxt, mlabel = MUTE_BG, MUTE_BDR, MUTE_TEXT, "Unmute"
    else:
        mbg, mbdr, mtxt, mlabel = WHITE, BORDER, (139, 126, 114), "Mute"
    draw.rounded_rectangle([176, y+5, 236, y+35], radius=6, fill=mbg, outline=mbdr)
    mw = draw.textlength(mlabel, font=F_BTN)
    draw.text(((176 + 236 - mw) // 2, y + 14), mlabel, font=F_BTN, fill=mtxt)

    # Notes button
    draw.rounded_rectangle([244, y+5, 304, y+35], radius=6, fill=WHITE, outline=BORDER)
    nw = draw.textlength("Notes", font=F_BTN)
    draw.text(((244 + 304 - nw) // 2, y + 14), "Notes", font=F_BTN, fill=(139, 126, 114))

    # Level bars
    def bar(rms, color):
        filled = int(min(rms * 20, 5))
        parts = [("█" * filled, color), ("░" * (5 - filled), MUTED_TEXT)]
        x = W - 24 - 80
        for txt, clr in parts:
            draw.text((x, y + 18), txt, font=F_SMALL, fill=clr)
            x += draw.textlength(txt, font=F_SMALL)

    if recording and not muted:
        draw.text((W - 24 - 90, y + 5), "YOU", font=F_TAG, fill=YOU_CLR)
        bar(0.6, YOU_CLR)
        draw.text((W - 24 - 90, y + 22), "THEM", font=F_TAG, fill=THEM_CLR)
        bar(0.2, THEM_CLR)
    else:
        draw.text((W - 24 - 90, y + 5), "YOU", font=F_TAG, fill=YOU_CLR)
        bar(0.0, YOU_CLR)
        draw.text((W - 24 - 90, y + 22), "THEM", font=F_TAG, fill=THEM_CLR)
        bar(0.0, THEM_CLR)

def draw_toast(draw, message, level="success"):
    tw = W - 48
    th = 46
    tx = 24
    ty = H - th - 20
    if level == "success":
        tbg, tbdr, tacc, ttxt = TOAST_BG, TOAST_BDR, TOAST_ACC, TOAST_TEXT
    else:
        tbg = (255, 245, 245); tbdr = (254, 202, 202)
        tacc = (239, 68, 68); ttxt = (153, 27, 27)
    draw.rounded_rectangle([tx, ty, tx+tw, ty+th], radius=6, fill=tbg, outline=tbdr)
    draw.rectangle([tx, ty, tx+3, ty+th], fill=tacc)
    draw.text((tx+14, ty+14), message, font=F_TOAST, fill=ttxt)

def draw_template_badge(draw, template_name):
    badge = f"Template: {template_name}"
    bw = draw.textlength(badge, font=F_SMALL) + 14
    draw.rounded_rectangle([24, 46, 24+bw, 62], radius=4,
                            fill=(230, 245, 243), outline=ACCENT)
    draw.text((31, 49), badge, font=F_SMALL, fill=ACCENT)

# ── make_frame ────────────────────────────────────────────────────

def make_frame(
    recording=False,
    muted=False,
    utterances=None,
    suggestion=None,
    toast=None,
    template="Generic",
    show_template_badge=False,
    partial_text=None,
):
    utterances = utterances or []
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw_accent_strip(img)

    # Header
    draw_header(draw, kb_text="KB: 142 chunks" if not recording else "")
    y = 50
    if show_template_badge:
        draw_template_badge(draw, template)
        y = 68

    draw.line([(0, y), (W, y)], fill=BORDER)
    y += 14

    # Suggestions
    draw_section_label(draw, y, "SUGGESTIONS")
    y += 16
    if suggestion:
        draw_suggestion_card(draw, y, suggestion[0], suggestion[1], suggestion[2])
        y += 84
    else:
        draw_empty_suggestions(draw, y)
        y += 24

    y += 10

    # Search
    draw_search(draw, y)
    y += 38
    draw_section_label(draw, y, "TRANSCRIPT")
    y += 16

    # Transcript area (fixed height)
    transcript_top = y
    transcript_h   = H - transcript_top - 80
    draw.rectangle([0, transcript_top, W, transcript_top + transcript_h], fill=BG)

    if not utterances and not partial_text:
        draw_empty_transcript(draw, transcript_top)
    else:
        ty2 = transcript_top + 6
        for speaker, text in utterances:
            row_h = draw_utterance(draw, ty2, speaker, text)
            ty2 += row_h
        if partial_text:
            draw.text((24, ty2 + 2), "…  " + partial_text, font=F_SMALL, fill=MUTED_TEXT)

    y = H - 68
    draw_separator(draw, y)
    y += 10

    rec_label = "⏹  Stop" if recording else "⏺  Record"
    draw_controls(draw, y, recording=recording, muted=muted, rec_label=rec_label)

    if toast:
        draw_toast(draw, toast[0], toast[1])

    return img


# ── Scene list ────────────────────────────────────────────────────

UTT = [
    ("you",  "So what's the plan for the discovery call today?"),
    ("them", "Walk them through the pain points, then show the prototype."),
    ("you",  "Got it. Should I lead with pricing or save it for later?"),
    ("them", "Save it. Get them talking first."),
]

SUGGESTION = (
    "Lead with open-ended questions",
    "Ask about current workflow before showing the product",
    "customer_discovery.md",
)

scenes = [
    # Idle
    dict(state=dict(), ms=1800),
    # Template badge appears
    dict(state=dict(show_template_badge=True, template="Customer Discovery"), ms=900),
    dict(state=dict(show_template_badge=True, template="Customer Discovery"), ms=600),
    # Record clicked
    dict(state=dict(recording=True, show_template_badge=True, template="Customer Discovery"), ms=500),
    # Processing
    dict(state=dict(recording=True, partial_text="So what's the plan…",
                    show_template_badge=True, template="Customer Discovery"), ms=700),
    # Utterances appear
    dict(state=dict(recording=True, utterances=UTT[:1],
                    show_template_badge=True, template="Customer Discovery"), ms=900),
    dict(state=dict(recording=True, utterances=UTT[:2],
                    show_template_badge=True, template="Customer Discovery"), ms=900),
    dict(state=dict(recording=True, utterances=UTT[:3],
                    show_template_badge=True, template="Customer Discovery"), ms=800),
    dict(state=dict(recording=True, utterances=UTT[:4],
                    show_template_badge=True, template="Customer Discovery"), ms=800),
    # Suggestion appears
    dict(state=dict(recording=True, utterances=UTT, suggestion=SUGGESTION,
                    show_template_badge=True, template="Customer Discovery"), ms=1400),
    # Mute
    dict(state=dict(recording=True, muted=True, utterances=UTT, suggestion=SUGGESTION,
                    show_template_badge=True, template="Customer Discovery"), ms=1000),
    dict(state=dict(recording=True, muted=True, utterances=UTT, suggestion=SUGGESTION,
                    show_template_badge=True, template="Customer Discovery"), ms=800),
    # Unmute
    dict(state=dict(recording=True, muted=False, utterances=UTT, suggestion=SUGGESTION,
                    show_template_badge=True, template="Customer Discovery"), ms=600),
    # Stop -> toast
    dict(state=dict(utterances=UTT, suggestion=SUGGESTION,
                    toast=("Session saved — 4 utterances", "success"),
                    show_template_badge=True, template="Customer Discovery"), ms=2200),
    # Back to idle
    dict(state=dict(), ms=1200),
]

# ── Render ────────────────────────────────────────────────────────

def main():
    out = os.path.join(os.path.dirname(__file__), "..", "demo_update.gif")

    print("Rendering frames…")
    frames = [make_frame(**s["state"]) for s in scenes]
    durations = [s["ms"] for s in scenes]

    print("Quantizing…")
    quant = [f.quantize(colors=128, method=Image.Quantize.MEDIANCUT) for f in frames]

    print("Saving GIF…")
    quant[0].save(
        out,
        save_all=True,
        append_images=quant[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )

    size_mb = os.path.getsize(out) / 1_000_000
    print(f"Saved {out}  ({size_mb:.2f} MB)")

    if size_mb > 5:
        print("Over 5 MB — retrying with 64 colors…")
        quant64 = [f.quantize(colors=64, method=Image.Quantize.MEDIANCUT) for f in frames]
        quant64[0].save(
            out,
            save_all=True,
            append_images=quant64[1:],
            duration=durations,
            loop=0,
            optimize=True,
        )
        size_mb = os.path.getsize(out) / 1_000_000
        print(f"Re-saved at 64 colors: {size_mb:.2f} MB")


if __name__ == "__main__":
    main()
