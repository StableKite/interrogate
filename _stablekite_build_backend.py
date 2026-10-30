"""Delegate to scikit-build-core without lingering Windows MSBuild workers."""
import os

from scikit_build_core import build as _backend


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    previous = os.environ.get("MSBUILDDISABLENODEREUSE")
    os.environ["MSBUILDDISABLENODEREUSE"] = "1"
    try:
        return _backend.build_wheel(wheel_directory, config_settings, metadata_directory)
    finally:
        if previous is None:
            os.environ.pop("MSBUILDDISABLENODEREUSE", None)
        else:
            os.environ["MSBUILDDISABLENODEREUSE"] = previous


def __getattr__(name):
    return getattr(_backend, name)
