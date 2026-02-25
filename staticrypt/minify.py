from minify_html import minify
import logging

logger = logging.getLogger(__name__)
    
def minify_html_content(html_content: str, verbose: bool = False) -> str:
    """Minify the given HTML content."""
    if verbose:
        logger.info("Minifying HTML content.")
    return minify(html_content, minify_js=True, minify_css=True)