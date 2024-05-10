def validate_text(text, exct = []):
    validate_text = []
    varity = set(('_', '*', '[', ']', '(', ')', '~', '`', '#', '+', '-', '=', '|', '{', '}', '.', '!', ">", "\\"))
    varity -= set(exct)
    for char in text:
        if char in varity:
            validate_text.append("\\")
        validate_text.append(char)
    return "".join(validate_text)
