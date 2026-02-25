import argparse
from importlib import resources
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from .md2html import convert_markdown_to_html
from .encrypt import encrypt_file, decrypt_file
from .minify import minify_html_content


def create_static_decrypt_html(encrypted_content: bytes, output_path: Path):
    """Generate a static HTML file with embedded encrypted content."""
    template = resources.files("staticrypt").joinpath("decrypt_template.html").read_text(
        encoding="utf-8"
    )
    filled_template = template.replace(
        "ENCRYPTED_CONTENT_PLACEHOLDER", str(list(encrypted_content))
    )
    output_path.write_text(filled_template, encoding="utf-8")


def get_package_version() -> str:
    try:
        return version("staticrypt")
    except PackageNotFoundError:
        return "unknown"


def main(args=None):
    import logging

    parser = argparse.ArgumentParser(description="StaticEncrypt CLI Tool")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"staticrypt {get_package_version()}",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Protect command
    protect_parser = subparsers.add_parser(
        "protect", help="Create an encrypted password-protected HTML file from a Markdown or HTML input."
    )
    protect_parser.add_argument(
        "-i",
        "--input",
        type=Path,
        required=True,
        help="Path to the input Markdown or HTML file.",
    )
    protect_parser.add_argument(
        "-p",
        "--password",
        type=str,
        required=True,
        help="Password for encryption.",
    )
    protect_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Optional path to the output HTML file. If omitted, a name will be generated in the input file directory.",
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
    protect_parser.add_argument(
        "--minify",
        nargs="?",
        const="true",
        type=str,
        choices=["true", "false", "1", "0"],
        default="true",
        help="Enable or disable HTML minification (default: true).",
    )

    # Encrypt command
    encrypt_parser = subparsers.add_parser("encrypt", help="Encrypt an HTML file.")
    encrypt_parser.add_argument(
        "-i",
        "--input",
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
        "-o",
        "--output",
        type=Path,
        help="Optional path to the output encrypted file. If omitted, a name will be generated in the current directory.",
    )
    encrypt_parser.add_argument(
        "--allow-unsafe-password",
        action="store_true",
        help="Skip password strength validation (unsafe).",
    )

    # Decrypt command
    decrypt_parser = subparsers.add_parser(
        "decrypt", help="Decrypt an encrypted HTML file."
    )
    decrypt_parser.add_argument(
        "-i",
        "--input",
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
    convert_parser = subparsers.add_parser(
        "convert", help="Convert a Markdown file to HTML."
    )
    convert_parser.add_argument(
        "-i",
        "--input",
        type=Path,
        required=True,
        help="Path to the input Markdown file.",
    )
    convert_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Optional path to the output HTML file. If omitted, a name will be generated in the current directory.",
    )
    convert_parser.add_argument(
        "--style",
        type=Path,
        help="Path to an optional CSS file to include in the HTML.",
    )
    convert_parser.add_argument(
        "--minify",
        nargs="?",
        const="true",
        type=str,
        choices=["true", "false", "1", "0"],
        default="true",
        help="Enable or disable HTML minification (default: true).",
    )

    if args is None:
        args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)

    # Ensure 'minify' is added to the args namespace for all commands
    args.minify = args.minify if hasattr(args, 'minify') else 'true'

    # Ensure 'minify' attribute exists in args
    minify = getattr(args, 'minify', False)

    if args.command == "protect":
        intermediate_html_path = None
        encrypted_path = None

        try:
            # Determine output location
            if args.output is None:
                default_name = f"{args.input.stem}.protected.html"
                args.output = args.input.parent / default_name

            logger.info(f"Output file: {args.output}")

            # Auto-infer file type
            input_extension = args.input.suffix.lower()
            if input_extension == ".md":
                # Convert Markdown to HTML
                markdown_content = args.input.read_text(encoding="utf-8")

                css_content = ""
                if args.style:
                    if not args.style.is_file():
                        parser.error(f"CSS file does not exist: {args.style}")
                    css_content = args.style.read_text(encoding="utf-8")

                minify = args.minify.lower() not in ["false", "0"]
                html_content = convert_markdown_to_html(
                    markdown_content, css_content, minify=minify
                )

                # Save intermediate HTML file
                intermediate_html_path = args.input.with_suffix(".intermediate.html")
                intermediate_html_path.write_text(html_content, encoding="utf-8")

            elif input_extension == ".html":
                # Handle HTML input directly
                intermediate_html_path = args.input

                if args.style:
                    if not args.style.is_file():
                        parser.error(f"CSS file does not exist: {args.style}")
                    css_content = args.style.read_text(encoding="utf-8")

                    # Inject CSS into HTML
                    html_content = intermediate_html_path.read_text(encoding="utf-8")
                    style_tag = f"<style>{css_content}</style>"
                    html_content = html_content.replace("</head>", f"{style_tag}</head>")

                    # Save modified HTML to a temporary file
                    intermediate_html_path = args.input.with_suffix(".styled.html")
                    intermediate_html_path.write_text(html_content, encoding="utf-8")

                # Minify the HTML content before encryption
                html_content = intermediate_html_path.read_text(encoding="utf-8")
                minified_html = minify_html_content(html_content)
                # Ensure the original input file is not overwritten
                if intermediate_html_path != args.input:
                    intermediate_html_path.write_text(minified_html, encoding="utf-8")
            else:
                logger.error(f"Unsupported file type: {input_extension}")
                raise ValueError("Unsupported file type. Only .md and .html are supported.")

            # Encrypt the HTML file
            try:
                encrypt_file(
                    intermediate_html_path,
                    args.password,
                    allow_unsafe=getattr(args, "allow_unsafe_password", False),
                )
            except ValueError:
                return
            except Exception as e:
                logger.error(f"Encryption failed: {e}")
                raise
            # Read the encrypted content
            encrypted_path = intermediate_html_path.with_name(
                f"{intermediate_html_path.stem}-encrypted.html"
            )
            encrypted_content = encrypted_path.read_bytes()

            # Create the static decrypt HTML file
            create_static_decrypt_html(encrypted_content, args.output)

            # Always minify the decrypt_template
            decrypt_template_content = args.output.read_text(encoding="utf-8")
            minified_template = minify_html_content(decrypt_template_content)
            args.output.write_text(minified_template, encoding="utf-8")
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        finally:
            # Clean up intermediate files
            if intermediate_html_path and intermediate_html_path.exists() and intermediate_html_path != args.input:
                intermediate_html_path.unlink()
            if encrypted_path and encrypted_path.exists():
                encrypted_path.unlink()

    elif args.command == "encrypt":
        try:
            encrypt_file(
                args.input,
                args.password,
                allow_unsafe=getattr(args, "allow_unsafe_password", False),
            )
        except ValueError:
            return
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise

    elif args.command == "decrypt":
        decrypt_file(args.input, args.password)

    elif args.command == "convert":
        input = args.input
        output = args.output or input.with_suffix(".html")
        style_file = args.style

        if not input.is_file():
            parser.error(f"Input file does not exist: {input}")

        css_content = ""
        if style_file:
            if not style_file.is_file():
                parser.error(f"CSS file does not exist: {style_file}")
            css_content = style_file.read_text(encoding="utf-8")

        markdown_content = input.read_text(encoding="utf-8")
        minify = args.minify.lower() not in ["false", "0"]
        html_content = convert_markdown_to_html(
            markdown_content, css_content, minify=minify
        )
        output.write_text(html_content, encoding="utf-8")
        print(f"Converted {input} to {output}")


if __name__ == "__main__":
    main()
