#!/bin/env python3

from utils import log

import argparse
import utils
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='vocab_cli', description='CLI para leer e insertar registros en Supabase.')

    sub = parser.add_subparsers(dest='command', required=True)

    # read
    p_read = sub.add_parser('read', help='Leer registros de la tabla.')
    p_read.add_argument('--page-size', type=int, default=1000, help='Tamaño de página para paginación REST.')
    p_read.add_argument('--limit', type=int, default=-1, help='Cuántas filas imprimir como muestra (0 imprime ninguna).')
    p_read.add_argument('-f', '--format', required=False, choices=['json', 'txt'], default='txt', help='Formats: json, txt')

    # insert
    p_ins = sub.add_parser('insert', help='Insertar un término en la tabla.')
    p_ins.add_argument('word', help='Término a insertar.')
    p_ins.add_argument('--level', required=True, choices=[lvl.value for lvl in utils.Level], help='Nivel (A1, A2, B1, B2, C1, C2).')

    # pick
    p_pick = sub.add_parser('pick', help='Seleccionar N términos aleatorios de la tabla.')
    p_pick.add_argument('n', type=int, help='Cantidad de términos a seleccionar.')
    p_pick.add_argument('-f', '--format', required=False, choices=['json', 'txt'], default='txt', help='Formats: json, txt')

    return parser


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()

    try:
        config = utils.load_environment_variables('.env')
        db_connection = utils.VocabularyDB(config)
    except Exception as e:
        log.error(str(e))
        sys.exit(1)

    if args.command == 'read' or args.command == 'pick':
        rows = db_connection.fetch_all_rows()

        print(f'Tabla: {db_connection.table_name()}')
        print(f'Total filas: {len(rows)}')

        if args.command == 'pick':
            rows = utils.pick_terms(rows, args.n)

        if args.format == 'json':
            limit = len(rows) if not hasattr(args, 'limit') or (hasattr(args, 'limit') and args.limit < 0) else args.limit

            for r in rows[:limit]:
                print(r)
        elif args.format == 'txt':
            print(f'Vocabulario: {", ".join([r["term"] for r in rows])}')

    elif args.command == 'insert':
        level = utils.Level(args.level)
        db_connection.insert_word(args.word, level)
        print(f'Insertado: term="{args.word}", level="{level.value}"')
