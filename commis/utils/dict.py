import collections

def deep_merge(*args):
    dest = {}
    stack = [(dest, d) for d in args]
    while stack:
        current_dest, current_src = stack.pop()
        for key, value in current_src.iteritems():
            if key not in current_dest:
                current_dest[key] = value
            else:
                if isinstance(value, collections.Mapping) and isinstance(current_dest[key], collections.Mapping):
                    stack.append((current_dest[key], value))
                else:
                    current_dest[key] = value
    return dest


def flatten_dict(data):
    return _flatten_each({}, data, ())


def _flatten_each(dest, data, key_path):
    if isinstance(data, collections.Mapping):
        for key, value in data.iteritems():
            _flatten_each(dest, value, key_path+(key,))
    elif isinstance(data, collections.Sequence) and not isinstance(data, basestring):
        for value in data:
            _flatten_each(dest, value, key_path)
    else:
        dest.setdefault('_'.join(key_path), []).append(data)
        dest.setdefault(key_path[-1], []).append(data)
    return dest
