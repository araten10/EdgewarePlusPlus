import sys

def is_linux():
    return 'linux' in sys.platform

def is_windows():
    return 'win32' in sys.platform

if is_linux():
    from .linux import *
elif is_windows():
    from .windows import *
else:
    raise RuntimeError('Unsupported operating system: {}'.format(sys.platform))
