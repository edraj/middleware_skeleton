from re import sub as re_sub


def camel_case(snake_str):
    words = snake_str.split("_")
    return "".join(word.title() for word in words)


def snake_case(camel_str):
    return re_sub(r"(?<!^)(?=[A-Z])", "_", camel_str).lower()


def escape_for_redis(s: str) -> str:
    return s.translate(
        str.maketrans(
            {".": r"\.", "@": r"\@", ":": r"\:", "/": r"\/", "-": r"\-", " ": r"\ "}
        )
    )
