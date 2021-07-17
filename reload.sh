pip uninstall -y aioproc
poetry build
pip install -q dist/aioproc-0.1.0-py3-none-any.whl
