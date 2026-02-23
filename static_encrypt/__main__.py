import argparse
from pathlib import Path
from md2html import convert_markdown_to_html
from encrypt import encrypt_file


def create_static_decrypt_html(encrypted_content: bytes, output_path: Path):
    """Generate a static HTML file with embedded encrypted content."""
    template = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Decrypt Embedded Content</title>
    <style>
        body {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
        }}
        .container {{
            text-align: center;
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        input[type=\"password\"] {{
            display: block;
            margin: 10px auto;
            padding: 10px;
            width: 80%;
            border: 1px solid #ccc;
            border-radius: 4px;
        }}
        button {{
            margin-top: 10px;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            background-color: #007BFF;
            color: white;
            cursor: pointer;
        }}
        button:hover {{
            background-color: #0056b3;
        }}
        #output {{
            margin-top: 20px;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            background: #f9f9f9;
            white-space: pre-wrap;
        }}
    </style>
</head>
<body>
    <div class=\"container\">
        <h1>Decrypt Content</h1>
        <input type=\"password\" id=\"password\" placeholder=\"Enter password\">
        <button onclick=\"decryptContent()\">Decrypt</button>
        <div id=\"output\"></div>
    </div>

    <script src=\"https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.1.1/crypto-js.min.js\"></script>
    <script>
        const encryptedContent = new Uint8Array({list(encrypted_content)});

        function decryptContent() {{
            const password = document.getElementById('password').value;
            const output = document.getElementById('output');

            if (!password) {{
                alert('Please provide a password.');
                return;
            }}

            try {{
                const salt = encryptedContent.slice(0, 16);
                const iv = encryptedContent.slice(16, 32);
                const ciphertext = encryptedContent.slice(32);

                const encoder = new TextEncoder();
                const keyMaterial = encoder.encode(password);
                window.crypto.subtle.importKey(
                    'raw',
                    keyMaterial,
                    {{ name: 'PBKDF2' }},
                    false,
                    ['deriveKey']
                ).then(baseKey => {{
                    return window.crypto.subtle.deriveKey(
                        {{
                            name: 'PBKDF2',
                            salt: salt,
                            iterations: 100000,
                            hash: 'SHA-256'
                        }},
                        baseKey,
                        {{ name: 'AES-CBC', length: 256 }},
                        false,
                        ['decrypt']
                    );
                }}).then(cryptoKey => {{
                    return window.crypto.subtle.decrypt(
                        {{ name: 'AES-CBC', iv: iv }},
                        cryptoKey,
                        ciphertext
                    );
                }}).then(decryptedBuffer => {{
                    const decoder = new TextDecoder();
                    const plaintext = decoder.decode(decryptedBuffer);

                    if (plaintext.trim().startsWith('<!DOCTYPE html>')) {{
                        const newWindow = window.open('', '_blank');
                        newWindow.document.write(plaintext);
                        newWindow.document.close();
                    }} else {{
                        output.textContent = plaintext;
                        throw new Error('Decrypted content is not valid HTML.');
                    }}
                }}).catch(error => {{
                    output.textContent = 'Error: ' + error.message;
                }});
            }} catch (error) {{
                output.textContent = 'Error: ' + error.message;
            }}
        }}
    </script>
</body>
</html>
"""
    output_path.write_text(template, encoding="utf-8")


def main():
    import logging

    parser = argparse.ArgumentParser(description="Convert, encrypt, and embed Markdown content.")
    parser.add_argument(
        "--markdown_file",
        type=Path,
        required=True,
        help="Path to the input Markdown file.",
    )
    parser.add_argument(
        "--password",
        type=str,
        required=True,
        help="Password for encryption.",
    )
    parser.add_argument(
        "--output_file",
        type=Path,
        help="Optional path to the output HTML file. If omitted, a name will be generated in the current directory.",
    )
    args = parser.parse_args()

    # Determine output location
    if args.output_file is None:
        default_name = f"{args.markdown_file.stem}.protected.html"
        args.output_file = Path.cwd() / default_name

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)

    logger.info(f"Output file: {args.output_file}")
    print(f"Output file: {args.output_file}")

    # Convert Markdown to HTML
    markdown_content = args.markdown_file.read_text(encoding="utf-8")
    html_content = convert_markdown_to_html(markdown_content)

    # Save intermediate HTML file
    intermediate_html_path = args.markdown_file.with_suffix(".html")
    intermediate_html_path.write_text(html_content, encoding="utf-8")

    # Encrypt the HTML file
    encrypt_file(intermediate_html_path, args.password)

    # Read the encrypted content
    encrypted_path = intermediate_html_path.with_name(f"{intermediate_html_path.stem}-encrypted.html")
    encrypted_content = encrypted_path.read_bytes()

    # Create the static decrypt HTML file
    create_static_decrypt_html(encrypted_content, args.output_file)

    # Clean up intermediate files
    intermediate_html_path.unlink()
    encrypted_path.unlink()


if __name__ == "__main__":
    main()