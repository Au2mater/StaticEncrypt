# StaticEncrypt

StaticEncrypt is a Python-based toolchain designed to help users host secure, password-protected static sites. It provides the following functionality:

1. **Markdown to HTML Conversion**: Converts Markdown files into HTML using the `md2html.py` script.
2. **HTML Encryption**: Encrypts HTML files with a password using the `encrypt.py` script, ensuring secure storage and transmission.
3. **Decryption via Static HTML**: Generates a static HTML file with embedded encrypted content that can be decrypted in the browser using JavaScript.

## Features
- **Secure Static Hosting**: Host password-protected static sites without requiring server-side processing.
- **Markdown Conversion**: Easily convert Markdown files to HTML.
- **Secure Encryption**: Protect your HTML content with AES encryption.
- **Browser-Based Decryption**: Decrypt and render encrypted content directly in the browser.

## Usage

### Protect Command
Use the `protect` command to convert, encrypt, and embed Markdown content into a password-protected static site:

```bash
python -m static_encrypt protect --markdown_file <path-to-markdown> --password <encryption-password>
```

### Encrypt Command
Use the `encrypt` command to encrypt an HTML file:

```bash
python -m static_encrypt encrypt --input_file <path-to-html> --password <encryption-password>
```

### Decrypt Command
Use the `decrypt` command to decrypt an encrypted HTML file:

```bash
python -m static_encrypt decrypt --input_file <path-to-encrypted-html> --password <encryption-password>
```

### Example
```bash
python -m static_encrypt protect --markdown_file ./resources/sample.md --password "YourPassword123"
```

This will:
1. Convert `sample.md` to HTML.
2. Encrypt the HTML with the provided password.
3. Generate a static HTML file (e.g., `sample.protected.html`) that can decrypt and display the content in the browser.

## Requirements
- Python 3.8+
- `cryptography` library
- `markdown` library

Install dependencies using:
```bash
pip install -r requirements.txt
```

## Folder Structure
- `static_encrypt/`
  - `md2html.py`: Markdown to HTML conversion.
  - `encrypt.py`: HTML encryption and decryption.
  - `__main__.py`: CLI tool for the full workflow.
- `resources/`: Sample files for testing.

## License
This project is licensed under the MIT License.