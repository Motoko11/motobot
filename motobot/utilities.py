def format_responses(iterable, format_string='{}', separator=', ', max_length=400):
    data = list(iterable)
    responses = []

    while data != []:
        cur = []
        length = len(format_string)

        while data != []:
            l = len(data[0]) + len(separator)
            if length + l <= max_length:
                length += l
                cur.append(data.pop(0))
            else:
                break

        msg = format_string.format(separator.join(cur))
        responses.append(msg)

    return responses
