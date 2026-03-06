"""
pipeline/subtitles.py
Generates ASS subtitle file — POP style (one word at a time, centred, animated)
"""

ASS_HEADER = """\
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Pop,Montserrat,115,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,7,0,5,0,0,200,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def _seconds_to_ass(seconds: float) -> str:
    cs = int(round(seconds * 100))
    h  = cs // 360000; cs %= 360000
    m  = cs // 6000;   cs %= 6000
    s  = cs // 100;    cs %= 100
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def generate_ass(word_timings: list[dict], output_path: str) -> str:
    """
    Writes ASS subtitle file — one word pops in at a time.
    Each word scales 130%→100% in 80ms (pop animation).
    Returns output_path.
    """
    lines = [ASS_HEADER]

    for timing in word_timings:
        word  = timing["word"].upper()
        start = _seconds_to_ass(timing["start"])
        end   = _seconds_to_ass(timing["end"])

        # Pop: scale from 130% down to 100% over 80ms
        pop = r"{\fscx130\fscy130\t(0,80,\fscx100\fscy100)}"
        lines.append(f"Dialogue: 0,{start},{end},Pop,,0,0,0,,{pop}{word}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return output_path
