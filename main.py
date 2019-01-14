import hashlib
from itertools import product
from string import ascii_lowercase
from time import time
from typing import Set, Generator, Optional

special_chars = '@_#'


def read_shadow(path: str) -> Set[str]:
    with open(path) as f:
        return {line.split(':')[1].split('$')[2] for line in f.read().split('\n') if ':' in line and not any(c in line for c in '!*')}


def generate_all_words(possible_chars: str, min_size: int, max_size: int) -> Generator[str, None, None]:
    for size in range(min_size, max_size + 1):
        for combination in product(*[possible_chars for _ in range(size)]):
            yield ''.join(combination)


def find_hash_original(algorithm, word_generator: Generator[str, None, None], targets, generator_size: Optional[int]=None):
    start = time()
    for i, tried_password in enumerate(word_generator):
        # print(tried_password)
        if generator_size and i % 10_000_000 == 0:
            print(f"{(i / generator_size) * 100}%  {round(i / (time() - start), 2)} opérations par secondes")
        hashed_tried_password = algorithm(str.encode(tried_password)).hexdigest()
        if hashed_tried_password in targets:
            print(f"{tried_password} découvert au bout de {round(time() - start, 2)} secondes à la {i}ème itération")
            targets.remove(hashed_tried_password)
            if len(targets) == 0:
                print("Tout les mots de passes ont été découverts")
                break
    print(f"Les hash {targets} n'ont pas pu être cassés. Temps total : {round(time() - start, 2)} secondes")


if __name__ == '__main__':
    chars = ascii_lowercase
    mini, maxi = 6, 6
    possible_combination_number = sum(len(chars) ** i for i in range(mini, maxi + 1))
    print(possible_combination_number / 10 ** 6, "millions de combinaisons possibles")
    find_hash_original(
        hashlib.md5,
        generate_all_words(chars, mini, maxi),
        read_shadow('shadow'),
        possible_combination_number
    )
