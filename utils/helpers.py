from re import sub as re_sub


def camel_case(snake_str: str) -> str:
    words: list[str] = snake_str.split("_")
    return "".join(word.title() for word in words)


def snake_case(camel_str: str) -> str:
    return re_sub(r"(?<!^)(?=[A-Z])", "_", camel_str).lower()


def escape_for_redis(s: str) -> str:
    table: dict[int, str] = str.maketrans(
        {".": r"\.", "@": r"\@", ":": r"\:", "/": r"\/", "-": r"\-", " ": r"\ "}
    )
    return s.translate(table)


def special_to_underscore(s: str) -> str:
    table: dict[int, str] = str.maketrans(
        {".": "_", "@": "_", ":": "_", "/": "_", "-": "_", " ": "_"}
    )
    return s.translate(table)
