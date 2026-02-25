import pytest
from staticrypt.__main__ import get_package_version, main
from pathlib import Path
import argparse
from shutil import copyfile

@pytest.mark.parametrize("input_file, expected_output", [
    ("resources/sample.md", "sample.protected.html"),
    ("resources/sample-html.html", "sample.protected.html"),
])
def test_protect_command(input_file, expected_output, tmp_path):
    """Test the protect command with both Markdown and HTML files."""
    output_file = tmp_path / expected_output

    # Copy the input file to the temporary directory
    input_path = tmp_path / Path(input_file).name
    copyfile(input_file, input_path)

    # Simulate argparse arguments
    args = argparse.Namespace(
        command="protect",
        input=input_path,
        password="testpassword",
        output=output_file,
        style=None,
        allow_unsafe_password=True
    )

    # Call the main function directly
    main(args)

    # Assert the output file was created
    assert output_file.exists(), f"Output file {output_file} was not created."

@pytest.mark.parametrize("unsupported_file", [
    "resources/sample.txt",
    "resources/sample.json",
])
def test_protect_command_unsupported_file(unsupported_file):
    """Test the protect command with unsupported file types."""
    args = argparse.Namespace(
        command="protect",
        input=Path(unsupported_file),
        password="testpassword",
        output=None,
        style=None,
        allow_unsafe_password=True
    )

    with pytest.raises(ValueError, match="Unsupported file type"):
        main(args)


def test_protect_default_output_in_input_directory(tmp_path, monkeypatch):
    """When output is omitted, protect writes next to the input file."""
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    input_path = input_dir / "sample.md"
    copyfile("resources/sample.md", input_path)

    other_cwd = tmp_path / "other-cwd"
    other_cwd.mkdir()
    monkeypatch.chdir(other_cwd)

    args = argparse.Namespace(
        command="protect",
        input=input_path,
        password="testpassword",
        output=None,
        style=None,
        allow_unsafe_password=True,
        minify="true",
    )

    main(args)

    expected_output = input_dir / "sample.protected.html"
    assert expected_output.exists(), f"Output file {expected_output} was not created."


def test_version_flag_outputs_package_version(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["staticrypt", "--version"])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 0
    output = capsys.readouterr().out.strip()
    assert output == f"staticrypt {get_package_version()}"