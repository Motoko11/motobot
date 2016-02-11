def split_response(iterable, format_string='{}', separator=', ', max_length=400):
    cur = ''
    
    for x in iterable:
        if len(cur) + len(format_string) + len(x) >= max_length:
            msg = format_string.format(cur)
            cur = ''
            yield msg
        cur += (separator if cur != '' else '') + x

    if cur != '':
        msg = format_string.format(cur)
        yield msg
