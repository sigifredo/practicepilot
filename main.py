#!/bin/env python3

from __future__ import annotations
from utils import log

import pathlib
import utils


if __name__ == '__main__':
    config = utils.load_environment_variables('.env')
    config['SYSTEM_PROMPT_PATH'] = pathlib.Path(utils.__file__).parent / config['SYSTEM_PROMPT_PATH']

    model = utils.Qwen()
    db_connection = utils.VocabularyDB(config)
    vocab_terms = db_connection.get_terms()

    if not vocab_terms:
        raise Exception('No se encontró vocabulario en la base de datos (columna "term").')

    log.info(f'Vocabulario cargado ({len(vocab_terms)} términos).')
    log.info(f'Modelo en: {model.device()}')
    log.info(f'Dtype: {model.dtype()}')
    log.info(f'Comandos:\n\t- "exit": para salir.\n\t- "next words": para practicar otro par de palabras.')
    print('\nModo práctica (pregunta-respuesta):\n- El sistema propone 1 ejercicio (ES -> EN)\n- Tú respondes\n- Te corrige y propone el siguiente\n')

    history: list[dict[str, str]] = []
    current_exercise: str | None = None
    student_answer: str | None = None
    target_terms = utils.pick_terms(vocab_terms, k=2)
    model.set_system_prompt(
        utils.build_prompt_from_file(
            config['SYSTEM_PROMPT_PATH'],
            {
                'vocab_csv': target_terms,
            },
        )
    )

    n = 1
    try:
        while True:
            current_exercise = model.run_prompt(utils.question_prompt())
            history.append({'exercise': current_exercise})

            print(f'\nEjercicio {n}\nPalabras a practicar: {", ".join(target_terms)}\nTraduce al inglés:')
            print(current_exercise)

            student_answer = input('\n\033[34mTu traducción:\033[0m ').strip()

            if not student_answer:
                continue

            if student_answer.lower() == 'exit':
                break

            if student_answer.lower() == 'next words':
                target_terms = utils.pick_terms(vocab_terms=vocab_terms, k=2)

                model.set_system_prompt(
                    utils.build_prompt_from_file(
                        config['SYSTEM_PROMPT_PATH'],
                        {
                            'vocab_csv': target_terms,
                        },
                    )
                )
                continue

            reply = model.run_prompt(utils.evaluate_answer(current_exercise, student_answer))

            print('\n\033[33m---\n\033[34mCorrección y retroalimentación:\033[0m\n')
            print('\n'.join(reply.splitlines()).strip())
            print('\n\033[33m---\033[0m')

            n += 1

    except (EOFError, KeyboardInterrupt):
        print('\nCerrando...')
