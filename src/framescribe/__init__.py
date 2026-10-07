"""FrameScribe — turn talk videos into diagrammatic, figure-aware Markdown notes."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

try:
    __version__ = _version("framescribe")
except PackageNotFoundError:  # running from a source checkout without install
    __version__ = "0.1.0"

__all__ = ["__version__"]
