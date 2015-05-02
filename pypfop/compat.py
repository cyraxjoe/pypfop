import sys

PY3 = sys.version_info[0] == 3

if PY3:
    BASE_STRING = str
else:
    BASE_STRING = basestring


def debug_msg(log, msg, label=''):
    if isinstance(msg, BASE_STRING):
        log.debug('{}: {}'.format(label, msg))
    else:
        log.debug('{}: {}'.format(label, msg.decode())) # bytes
