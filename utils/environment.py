import os
import pathlib


def load_environment_variables(env_path: str | pathlib.Path) -> dict[str, str]:
    env_path = pathlib.Path(env_path)

    if not env_path.is_file():
        return {}

    variables: dict[str, str] = {}

    for raw_line in env_path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()

        if not line or line.startswith('#'):
            continue

        if '=' not in line:
            continue

        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip()

        if not key:
            continue

        if len(value) >= 2 and value[0] == value[-1] and value[0] in {''', '''}:
            value = value[1:-1]

        os.environ[key] = value
        variables[key] = value

    return variables
