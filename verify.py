
# NOT thread-safe
def verify_key(key):
    key_ok = False
    with open('./keys.list') as f:
        cont = f.read()
    lines = []
    for line in cont.split('\n'):
        if line == '':
            continue
        if line == key and not key_ok:
            key_ok = True
            print('key {} is accepted.'.format(key))
        else:
            lines.append(line)
    if key_ok:
        with open('./keys.list', 'w+') as f:
            f.write('\n'.join(lines))
    return key_ok


