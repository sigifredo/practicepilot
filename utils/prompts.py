from typing import Mapping, Any, Union

import pathlib


def build_prompt_from_file(
    prompt_path: Union[str, pathlib.Path],
    variables: Mapping[str, Any],
) -> str:
    prompt_path = pathlib.Path(prompt_path)

    if not prompt_path.is_file():
        raise FileNotFoundError(f'Archivo no encontrado: {prompt_path}')

    prompt_template = prompt_path.read_text(encoding='utf-8')

    return prompt_template.format(**variables)


def evaluate_answer(exercise: str, answer: str) -> str:
    return ''.join(
        [
            'We are in an ongoing exercise session.\n',
            f'Previous exercise (Spanish): {exercise}\n',
            f'Student translation (English): {answer}\n\n',
            'Now do the following:\n',
            '1) Correct the student\'s translation. Provide brief, specific feedback and a short explanation of errors.\n',
            '2) Explicitly mention which target vocabulary term(s) were practiced.\n',
        ]
    )


def question_prompt() -> str:
    return 'Present one Spanish sentence for the student to translate into English.\nDo not include solutions.\n'
