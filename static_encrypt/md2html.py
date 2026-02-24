#!/usr/bin/env python3
"""Minimal type-safe markdown to HTML converter.

Usage:
    python md2html.py input.md output.html

This script reads a markdown file and writes a basic HTML conversion. It uses the
`markdown` package from PyPI for simplicity and enforces type hints for clarity.
"""

from __future__ import annotations

from pathlib import Path
import re
import html

import markdown
import markdown.extensions.extra
import markdown.extensions.admonition
import markdown.extensions.md_in_html


def preprocess_markdown(markdown_text: str) -> str:
    """Preprocess markdown text to handle custom syntax like checkboxes and strikethrough."""
    # Replace [ ] and [x] with input checkboxes
    markdown_text = re.sub(r"\[ \]", '<input type="checkbox">', markdown_text)
    markdown_text = re.sub(r"\[x\]", '<input type="checkbox" checked>', markdown_text)

    # Replace ~~text~~ with <del>text</del>
    markdown_text = re.sub(r"~~(.*?)~~", lambda m: f"<del>{m.group(1)}</del>", markdown_text)

    return markdown_text


def convert_markdown_to_html(markdown_text: str, css_content: str = "") -> str:
    """Convert markdown string to HTML with optional CSS.

    Args:
        markdown_text: A markdown-formatted string.
        css_content: A string containing CSS to embed in the HTML.

    Returns:
        A string of HTML wrapped in a full document.
    """

    # Preprocess markdown for custom syntax
    markdown_text = preprocess_markdown(markdown_text)

    # Enable the 'tables', 'extra', and 'admonition' extensions for proper rendering
    title = "Markdown Conversion"
    for line in markdown_text.splitlines():
        m = re.match(r"^\s*#\s+(.*)", line)
        if m:
            title = m.group(1).strip()
            break

    body_html = markdown.markdown(
        markdown_text,
        extensions=["tables", "extra", "admonition", "md_in_html"]
    )

    style_tag = f"<style>{css_content}</style>\n" if css_content else ""

    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '  <meta charset="utf-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"  <title>{html.escape(title)}</title>\n"
        f"  {style_tag}"
        "</head>\n"
        "<body>\n"
        f"{body_html}\n"
        "</body>\n"
        "</html>\n"
    )


def main() -> None:
    """Entry point for the script.

    Parses command-line arguments and performs conversion.
    """

    import argparse

    parser = argparse.ArgumentParser(description="Convert a Markdown file to HTML.")
    parser.add_argument(
        "-i", "--input",
        type=Path,
        help="Path to the input markdown file",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Path for the generated HTML file",
    )
    parser.add_argument(
        "--style",
        type=Path,
        help="Path to an optional CSS file to include in the HTML.",
    )
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output
    style_path = args.style

    if not input_path.is_file():
        parser.error(f"Input file does not exist: {input_path}")

    css_content = ""
    if style_path:
        if not style_path.is_file():
            parser.error(f"CSS file does not exist: {style_path}")
        css_content = style_path.read_text(encoding="utf-8")

    markdown_content = input_path.read_text(encoding="utf-8")
    html_content = convert_markdown_to_html(markdown_content, css_content)
    output_path.write_text(html_content, encoding="utf-8")


if __name__ == "__main__":
    main()
