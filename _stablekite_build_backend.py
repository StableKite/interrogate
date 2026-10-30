"""Delegate to scikit-build-core without lingering Windows MSBuild workers."""
import os

from scikit_build_core import build as _backend


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    scoped = {"MSBUILDDISABLENODEREUSE": "1"}
    if os.name == "nt":
        # The SDK is self-contained. An ambient vcpkg toolchain also installs
        # post-build deployment helpers into this temporary build tree.
        scoped["CMAKE_TOOLCHAIN_FILE"] = None
    previous = {name: os.environ.get(name) for name in scoped}
    for name, value in scoped.items():
        if value is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = value
    try:
        return _backend.build_wheel(wheel_directory, config_settings, metadata_directory)
    finally:
        for name, value in previous.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def __getattr__(name):
    return getattr(_backend, name)
