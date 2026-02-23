from static_encrypt import md2html


def test_title_from_h1(tmp_path):
    md = """# My Page\n\nSome content."""
    html = md2html.convert_markdown_to_html(md)
    assert "<title>My Page</title>" in html


def test_default_title_when_no_h1(tmp_path):
    md = """## Subtitle\n\nNo h1 here."""
    html = md2html.convert_markdown_to_html(md)
    assert "<title>Markdown Conversion</title>" in html
