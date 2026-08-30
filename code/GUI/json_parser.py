import json

def parse_json(buffer):
    parsed_objects = []
    start = None
    brace_count = 0

    i = 0
    while i < len(buffer):
        ch = buffer[i]

        if ch == '{':
            if start is None:
                start = i
            brace_count += 1
        elif ch == '}':
            brace_count -= 1
            if brace_count == 0 and start is not None:
                json_str = buffer[start:i+1]
                try:
                    parsed = json.loads(json_str)
                    parsed_objects.append(parsed)
                except json.JSONDecodeError:
                    pass
                # reset
                start = None
        i += 1

    # restbuffer (wat nog niet volledig is)
    if start is not None and brace_count > 0:
        buffer = buffer[start:]
    else:
        buffer = ""

    return parsed_objects, buffer
