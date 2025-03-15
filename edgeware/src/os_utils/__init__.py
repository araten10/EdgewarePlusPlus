import platform


def is_linux():
    return platform.system() == "Linux"


def is_windows():
    return platform.system() == "Windows"


def is_mac():
    return platform.system() == "Darwin"


if is_linux():
    from os_utils.linux import *  # noqa: F403
elif is_windows():
    from os_utils.windows import *  # noqa: F403
elif is_mac():
    from os_utils.mac import *  # noqa: F403
else:
    raise RuntimeError(f"Unsupported operating system: {platform.system()}")
