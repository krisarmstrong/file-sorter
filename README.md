# FileSorter

[![CI](https://github.com/krisarmstrong/file-sorter/actions/workflows/ci.yml/badge.svg)](https://github.com/krisarmstrong/file-sorter/actions)
[![Coverage](https://img.shields.io/badge/coverage-80%25-green)](https://github.com/krisarmstrong/file-sorter)
[![PyPI](https://img.shields.io/pypi/v/file-sorter.svg)](https://pypi.org/project/file-sorter/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/krisarmstrong/file-sorter/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)

Organizes files in a source directory into categorized subfolders by MIME type or extension.

## Installation

```bash
git clone https://github.com/krisarmstrong/file-sorter
cd file-sorter
pip install -r requirements.txt
```

## Usage

```bash
python file_sorter.py --source ~/Downloads --target ~/Documents --mode mime --verbose
python file_sorter.py --source ~/Downloads --target ~/Documents --mode extension --rename
```

- `--source`: Source directory (default: ~/Downloads).
- `--target`: Target directory for subfolders (default: ~/Documents).
- `--mode`: Sorting mode (mime or extension, default: mime).
- `--rename`: Add YYYY-MM- prefix (default for extension mode).
- `-v, --verbose`: Enable verbose logging.
- `--logfile`: Log file path (default: file_sorter.log).

## Files

- `file_sorter.py`: Main script.
- `version_bumper.py`: Version management tool.
- `tests/test_file_sorter.py`: Pytest suite.
- `requirements.txt`: Dependencies.
- `CHANGELOG.md`: Version history.
- `LICENSE`: MIT License.
- `CONTRIBUTING.md`: Contribution guidelines.
- `CODE_OF_CONDUCT.md`: Contributor Covenant.

## GitHub Setup

```bash
gh repo create file-sorter --public --source=. --remote=origin
git init
git add .
git commit -m "Initial commit: FileSorter v1.0.1"
git tag v1.0.1
git push origin main --tags
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT License. See [LICENSE](LICENSE) for details.