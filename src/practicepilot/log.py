def debug(s: str) -> None:
    print(f"[DEBUG] {s}")


def info(s: str) -> None:
    print(f"\033[32m[INFO]\033[0m {s}")


def warning(s: str) -> None:
    print(f"\033[33m[WARNING]\033[0m {s}")


def error(s: str) -> None:
    print(f"\033[31m[ERROR]\033[0m {s}")
