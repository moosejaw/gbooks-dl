import sys


def _check_writable(out):
    assert hasattr(out, 'write'), 'Custom print output object must have "write" method.'


def _log(msg, out):
    if hasattr(out, 'buffer'):
        msg_bytes = msg.encode()
        out.buffer.write(msg_bytes)
    else:
        _check_writable(out)
        out.write(msg)


def log_out(msg, out=None):
    if out is None:
        out = sys.stdout

    _log(msg, out)


def log_err(msg, out=None):
    if out is None:
        out = sys.stderr

    _log(msg, out)
