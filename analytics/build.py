"""Assemble all story outputs into a single static HTML dashboard.

Reads markdown + PNG from analytics/output/, embeds charts as base64 data URIs,
and writes a self-contained HTML file.

Run:    python build.py
Output: ../for-frank-and-brittney/demo/index.html
"""

import base64
import re
from pathlib import Path

import markdown as md_lib

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
DEMO_DIR = Path(__file__).resolve().parent.parent / "for-frank-and-brittney" / "demo"


def md_to_html_with_embedded_images(md_path: Path) -> str:
    """Convert a markdown file to HTML, replacing image refs with base64."""
    text = md_path.read_text()

    def embed_image(match):
        alt = match.group(1)
        img_name = match.group(2)
        img_path = md_path.parent / img_name
        if img_path.exists():
            b64 = base64.b64encode(img_path.read_bytes()).decode()
            return f'<img src="data:image/png;base64,{b64}" alt="{alt}" class="story-chart" />'
        return match.group(0)

    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", embed_image, text)
    html = md_lib.markdown(text, extensions=["tables", "fenced_code"])
    return html


HTML_TEMPLATE = """\
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Market Analytics Demo</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Serif:ital,wght@0,400;0,500;1,400&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet" />
  <style>
    :root {{
      --bg: #f8f7f5;
      --card-bg: #ffffff;
      --text: #2c3540;
      --muted: #6b7280;
      --accent: #0f5f4d;
      --accent2: #b07a2a;
      --accent3: #3f4f75;
      --border: #e5e5e0;
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: 'IBM Plex Serif', Georgia, serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.65;
      -webkit-font-smoothing: antialiased;
    }}
    .page {{
      max-width: 900px;
      margin: 0 auto;
      padding: 2rem 1.5rem 4rem;
    }}
    .masthead {{
      border-bottom: 3px solid var(--accent);
      padding-bottom: 1.5rem;
      margin-bottom: 3rem;
    }}
    .masthead h1 {{
      font-family: 'IBM Plex Sans', sans-serif;
      font-weight: 600;
      font-size: 1.75rem;
      color: var(--text);
      margin-bottom: 0.5rem;
    }}
    .masthead .subtitle {{
      font-size: 0.95rem;
      color: var(--muted);
    }}
    .story {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 2rem 2rem 1.5rem;
      margin-bottom: 2.5rem;
      position: relative;
    }}
    .story::before {{
      content: '';
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 4px;
      border-radius: 6px 0 0 6px;
    }}
    .story:nth-child(4n+1)::before {{ background: var(--accent); }}
    .story:nth-child(4n+2)::before {{ background: var(--accent2); }}
    .story:nth-child(4n+3)::before {{ background: var(--accent3); }}
    .story:nth-child(4n+4)::before {{ background: #7a4a4a; }}
    .story h1 {{
      font-family: 'IBM Plex Sans', sans-serif;
      font-size: 1.35rem;
      font-weight: 600;
      margin-bottom: 0.75rem;
    }}
    .story h2 {{
      font-family: 'IBM Plex Sans', sans-serif;
      font-size: 1.05rem;
      font-weight: 600;
      margin: 1.5rem 0 0.5rem;
      color: var(--text);
    }}
    .story p {{
      margin-bottom: 0.75rem;
      font-size: 0.95rem;
    }}
    .story-chart {{
      width: 100%;
      max-width: 100%;
      height: auto;
      margin: 1.25rem 0;
      border-radius: 4px;
    }}
    .story table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
      font-family: 'IBM Plex Sans', sans-serif;
      margin: 1rem 0;
    }}
    .story th {{
      background: var(--bg);
      border-bottom: 2px solid var(--border);
      padding: 0.5rem 0.75rem;
      text-align: left;
      font-weight: 600;
      white-space: nowrap;
    }}
    .story td {{
      border-bottom: 1px solid var(--border);
      padding: 0.4rem 0.75rem;
      white-space: nowrap;
    }}
    .story td:nth-child(n+2), .story th:nth-child(n+2) {{
      text-align: right;
    }}
    .story strong {{ font-weight: 600; }}
    .story ul, .story ol {{
      margin: 0.5rem 0 0.75rem 1.25rem;
      font-size: 0.95rem;
    }}
    .footer {{
      text-align: center;
      font-size: 0.8rem;
      color: var(--muted);
      padding-top: 2rem;
      border-top: 1px solid var(--border);
    }}
    .footer .ai-badge {{
      display: inline-block;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 3px;
      padding: 0.2rem 0.5rem;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 0.7rem;
      margin-top: 0.5rem;
    }}
    @media (max-width: 640px) {{
      .page {{ padding: 1rem; }}
      .story {{ padding: 1.25rem; }}
      .story table {{ font-size: 0.75rem; }}
      .story td, .story th {{ padding: 0.3rem 0.5rem; }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <div class="masthead">
      <h1>Market Analytics Demo</h1>
      <p class="subtitle">AI-assembled market view from public federal data · {date}</p>
    </div>
    {stories}
    <div class="footer">
      <p>Built from HUD LIHTC, HUD Fair Market Rents, HUD Income Limits, and IRS Migration data.</p>
      <span class="ai-badge">AI-generated analysis</span>
    </div>
  </div>
</body>
</html>
"""


def main():
    try:
        import markdown  # noqa: F401
    except ImportError:
        import subprocess, sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "markdown"])

    DEMO_DIR.mkdir(parents=True, exist_ok=True)

    story_files = sorted(OUTPUT_DIR.glob("*.md"))
    stories_html = []
    for md_path in story_files:
        html = md_to_html_with_embedded_images(md_path)
        stories_html.append(f'<section class="story">\n{html}\n</section>')

    from datetime import date
    page = HTML_TEMPLATE.format(
        date=date.today().isoformat(),
        stories="".join(stories_html),
    )

    out = DEMO_DIR / "index.html"
    out.write_text(page)
    print(f"Dashboard written to: {out}")
    print(f"Stories included: {len(stories_html)}")
    size_kb = out.stat().st_size / 1024
    print(f"File size: {size_kb:.0f} KB")


if __name__ == "__main__":
    main()
