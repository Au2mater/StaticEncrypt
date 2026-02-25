# StatiCrypt

StatiCrypt is a CLI tool designed to help users host secure, password-protected static sites including markdown content. 

![alt text](resources/screenshot.png)

It provides the following functionality:

1. **HTML/Markdown Encryption**: Locally encrypts any HTML or Markdown document with a user-provided password.
2. **Decryption via password**: Embeds the encrypted content in a static HTML file wrapper that allows any user to decrypt and preview it in the browser provided the correct password. The password itself is never stored in the HTML file.
3. **Markdown to HTML Conversion**: Converts Markdown files into HTML.
4. **Custom Styling**: Allows users to apply custom CSS styles to the generated HTML content.

## Features
- **Secure Static Hosting**: Host password-protected static sites without requiring server-side processing.
- **Markdown Conversion**: Easily convert Markdown files to HTML.
- **Secure Encryption**: Protect your HTML content with AES encryption.
- **Browser-Based Decryption**: Decrypt and render encrypted content directly in the browser, client side.

## Usage

### Protect Command
Use the `protect` command to convert, encrypt, and embed Markdown or HTML content into a password-protected static site:

```bash
# with uvx - no installation required
uvx staticrypt@latest protect \
    -i <path-to-input> \
    --password <encryption-password> \
    -o <path-to-output> \
    [--style <path-to-css>] \
    [--allow-unsafe-password]

# with pip:
pip install staticrypt
staticrypt protect \
    -i <path-to-input> \
    --password <encryption-password> \
    -o <path-to-output> \
    [--style <path-to-css>] \
    [--allow-unsafe-password]

```

- `<path-to-input>`: Path to the input file. Can be a Markdown (`.md`) or HTML (`.html`) file.
- `--style`: Optional. Path to a CSS file to style the generated HTML. For Markdown files, the CSS is applied during the conversion to HTML. For HTML files, the CSS is directly injected into the `<head>` section.
- `--allow-unsafe-password`: Optional. Skip strength validation on the supplied password. **Use with caution**; weak passwords are insecure.

### Convert Command
Use the `convert` command to convert a Markdown file to HTML:

```bash
python -m staticrypt convert -i <path-to-markdown> [-o <path-to-html>] [--style <path-to-css>]
```

- `--style`: Optional. Path to a CSS file to style the generated HTML.

### Encrypt Command
Use the `encrypt` command to encrypt an HTML file:

```bash
python -m staticrypt encrypt \
    -i <path-to-html> \
    --password <encryption-password> \
    [--allow-unsafe-password]
```

- `--allow-unsafe-password`: Optional. Skip strength validation on the supplied password. **Use with caution**.
### Decrypt Command
Use the `decrypt` command to decrypt an encrypted HTML file:

```bash
python -m staticrypt decrypt -i <path-to-encrypted-html> --password <encryption-password>
```

### Example
```bash
python -m staticrypt protect -i ./resources/sample.md --password "YourPassword123" --style ./resources/style.css
```

This will:
1. Convert `sample.md` to HTML.
2. Encrypt the HTML with the provided password.
3. Generate a static HTML file (e.g., `sample.protected.html`) that can decrypt and display the content in the browser.

## Requirements
- UV
- Python 3.8+
- `cryptography` library
- `markdown` library

```bash
uv sync
```

## Contributing

Contributions are welcome! If you encounter issues or have suggestions for improvement, please open an issue or submit a pull request.



```shell
# Clone the repository 
git clone https://github.com/Au2mater/StatiCrypt.git

# installing StatiCrypt locally for development:
uv sync --dev
uv pip install -e .

# run StatiCrypt with the example file:
staticrypt --help
staticrypt protect -i ./resources/sample.md --password "YourPassword123!" --style ./resources/style.css

# run tests:
pytest 

# uninstall StatiCrypt after development:
uv pip uninstall staticrypt
```



## License<a id="license"></a>

This repository is licensed under the [MIT License](LICENSE). See the LICENSE file for more details.