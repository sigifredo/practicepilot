import enum
import math
import random
import supabase
import typing


TABLE_NAME = 'vocabulary'


class Level(str, enum.Enum):
    A1 = 'A1'
    A2 = 'A2'
    B1 = 'B1'
    B2 = 'B2'
    C1 = 'C1'
    C2 = 'C2'


def pick_terms(vocab_terms: list[dict[str, typing.Any]], k: int) -> list[dict[str, typing.Any]]:
    '''
    Weighted random sample without replacement.
    Lower review_count => higher probability.

    Uses Efraimidis-Spirakis (A-ExpJ) sampling:
      key_i = -log(U) / w_i
    pick k items with smallest keys.
    '''

    if not vocab_terms or k <= 0:
        return []

    k = min(k, len(vocab_terms))

    def weight(item: dict[str, typing.Any]) -> float:
        rc = item.get('review_count', 0)

        try:
            rc = int(rc)
        except (TypeError, ValueError):
            rc = 0

        rc = max(rc, 0)

        return 1.0 / (rc + 1)

    scored = []

    for item in vocab_terms:
        w = weight(item)

        if w <= 0:
            continue

        u = random.random()
        key = -math.log(u) / w
        scored.append((key, item))

    if not scored:
        return []

    scored.sort(key=lambda x: x[0])
    picked = [item for _, item in scored[:k]]

    return picked


class VocabularyDB:
    def __init__(self, config: dict[str, str]):
        if not config.get('DB_API_KEY') or not config.get('DB_URL'):
            raise RuntimeError('No se han identificado las variables de acceso a la base de datos (DB_URL, DB_API_KEY).')

        self.db_client = supabase.create_client(config['DB_URL'], config['DB_API_KEY'])

    def get_terms(self):
        terms: list[str] = []
        rows: list[dict[str, typing.Any]] = self.fetch_all_rows()

        for row in rows:
            term = row.get('term')

            if term is None:
                continue

            term = str(term).strip()

            if term:
                terms.append(term)

        # dedupe preserving order
        seen = set()
        out = []

        for t in terms:
            if t not in seen:
                seen.add(t)
                out.append(t)

        return out

    def fetch_all_rows(self, page_size: int = 1000):
        all_rows = []
        start = 0

        while True:
            end = start + page_size - 1
            resp = self.db_client.table(TABLE_NAME).select('*').range(start, end).execute()

            if resp.data is None:
                raise RuntimeError(f'Respuesta sin data. Error: {resp}')

            batch = resp.data
            all_rows.extend(batch)

            if len(batch) < page_size:
                break

            start += page_size

        return all_rows

    def insert_word(self, word: str, level: Level) -> None:
        data = {
            'level': level.value,
            'term': word,
        }

        return self.db_client.table(TABLE_NAME).insert(data).execute()

    def table_name(self):
        return TABLE_NAME
