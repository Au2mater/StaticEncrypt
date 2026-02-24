import argparse
from pathlib import Path
from .md2html import convert_markdown_to_html
from .encrypt import encrypt_file, decrypt_file


def create_static_decrypt_html(encrypted_content: bytes, output_path: Path):
    """Generate a static HTML file with embedded encrypted content."""
    template_path = Path(__file__).parent / "decrypt_template.html"
    template = template_path.read_text(encoding="utf-8")
    filled_template = template.replace("ENCRYPTED_CONTENT_PLACEHOLDER", str(list(encrypted_content)))
    output_path.write_text(filled_template, encoding="utf-8")


def main():
    import logging

    parser = argparse.ArgumentParser(description="StaticEncrypt CLI Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Protect command
    protect_parser = subparsers.add_parser("protect", help="Convert, encrypt, and embed Markdown content.")
    protect_parser.add_argument(
        "-i", "--input",
        type=Path,
        required=True,
        help="Path to the input Markdown file.",
    )
    protect_parser.add_argument(
        "--password",
        type=str,
        required=True,
        help="Password for encryption.",
    )
    protect_parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Optional path to the output HTML file. If omitted, a name will be generated in the current directory.",
    )
    protect_parser.add_argument(
        "--style",
        type=Path,
        help="Path to an optional CSS file to include in the HTML.",
    )
    protect_parser.add_argument(
        "--allow-unsafe-password",
        action="store_true",
        help="Skip password strength validation when encrypting (unsafe).",
    )

    # Encrypt command
    encrypt_parser = subparsers.add_parser("encrypt", help="Encrypt an HTML file.")
    encrypt_parser.add_argument(
        "-i", "--input",
        type=Path,
        required=True,
        help="Path to the input HTML file.",
    )
    encrypt_parser.add_argument(
        "--password",
        type=str,
        required=True,
        help="Password for encryption.",
    )
    encrypt_parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Optional path to the output encrypted file. If omitted, a name will be generated in the current directory.",
    )
    encrypt_parser.add_argument(
        "--allow-unsafe-password",
        action="store_true",
        help="Skip password strength validation (unsafe).",
    )

    # Decrypt command
    decrypt_parser = subparsers.add_parser("decrypt", help="Decrypt an encrypted HTML file.")
    decrypt_parser.add_argument(
        "-i", "--input",
        type=Path,
        required=True,
        help="Path to the encrypted HTML file.",
    )
    decrypt_parser.add_argument(
        "--password",
        type=str,
        required=True,
        help="Password for decryption.",
    )

    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert a Markdown file to HTML.")
    convert_parser.add_argument(
        "-i", "--input",
        type=Path,
        required=True,
        help="Path to the input Markdown file.",
    )
    convert_parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Optional path to the output HTML file. If omitted, a name will be generated in the current directory.",
    )
    convert_parser.add_argument(
        "--style",
        type=Path,
        help="Path to an optional CSS file to include in the HTML.",
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)

    if args.command == "protect":
        intermediate_html_path = None
        encrypted_path = None

        try:
            # Determine output location
            if args.output is None:
                default_name = f"{args.input.stem}.protected.html"
                args.output = Path.cwd() / default_name

            logger.info(f"Output file: {args.output}")

            # Convert Markdown to HTML
            markdown_content = args.input.read_text(encoding="utf-8")

            css_content = ""
            if args.style:
                if not args.style.is_file():
                    parser.error(f"CSS file does not exist: {args.style}")
                css_content = args.style.read_text(encoding="utf-8")

            html_content = convert_markdown_to_html(markdown_content, css_content)

            # Save intermediate HTML file
            intermediate_html_path = args.input.with_suffix(".html")
            intermediate_html_path.write_text(html_content, encoding="utf-8")

            # Encrypt the HTML file
            encrypt_file(
                intermediate_html_path,
                args.password,
                allow_unsafe=getattr(args, "allow_unsafe_password", False),
            )

            # Read the encrypted content
            encrypted_path = intermediate_html_path.with_name(f"{intermediate_html_path.stem}-encrypted.html")
            encrypted_content = encrypted_path.read_bytes()

            # Create the static decrypt HTML file
            create_static_decrypt_html(encrypted_content, args.output)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        finally:
            # Clean up intermediate files
            if intermediate_html_path and intermediate_html_path.exists():
                intermediate_html_path.unlink()
            if encrypted_path and encrypted_path.exists():
                encrypted_path.unlink()

    elif args.command == "encrypt":
        encrypt_file(
            args.input_file,
            args.password,
            allow_unsafe=getattr(args, "allow_unsafe_password", False),
        )

    elif args.command == "decrypt":
        decrypt_file(args.input_file, args.password)

    elif args.command == "convert":
        input_file = args.input_file
        output = args.output or input_file.with_suffix(".html")
        style_file = args.style

        if not input_file.is_file():
            parser.error(f"Input file does not exist: {input_file}")

        css_content = ""
        if style_file:
            if not style_file.is_file():
                parser.error(f"CSS file does not exist: {style_file}")
            css_content = style_file.read_text(encoding="utf-8")

        markdown_content = input_file.read_text(encoding="utf-8")
        html_content = convert_markdown_to_html(markdown_content, css_content)
        output.write_text(html_content, encoding="utf-8")
        print(f"Converted {input_file} to {output}")


if __name__ == "__main__":
    main()