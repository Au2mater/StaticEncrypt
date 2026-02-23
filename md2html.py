#!/usr/bin/env python3
"""Minimal type-safe markdown to HTML converter.

Usage:
    python md2html.py input.md output.html

This script reads a markdown file and writes a basic HTML conversion. It uses the
`markdown` package from PyPI for simplicity and enforces type hints for clarity.
"""

from __future__ import annotations

from pathlib import Path

import markdown


def convert_markdown_to_html(markdown_text: str) -> str:
    """Convert markdown string to HTML.

    Args:
        markdown_text: A markdown-formatted string.

    Returns:
        A string of HTML wrapped in a full document.
    """

    # Base HTML document with DOCTYPE, head, and body container.  We don't
    # attempt to be fancy; the markdown library handles the markup for the
    # contents.
    body_html = markdown.markdown(markdown_text)

    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '  <meta charset="utf-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "  <title>Markdown Conversion</title>\n"
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
        "input",
        type=Path,
        help="Path to the input markdown file",
    )
    parser.add_argument(
        "output",
        type=Path,
        help="Path for the generated HTML file",
    )
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output

    if not input_path.is_file():
        parser.error(f"input file does not exist: {input_path}")

    markdown_content = input_path.read_text(encoding="utf-8")
    html_content = convert_markdown_to_html(markdown_content)
    output_path.write_text(html_content, encoding="utf-8")


if __name__ == "__main__":
    main()
