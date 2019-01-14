import hashlib
from itertools import product
from multiprocessing import Process
from string import ascii_lowercase
from time import time
from typing import Set, Generator, Iterable

Generator = Generator[str, None, None]

special_chars = '@_#'


def read_shadow(path: str) -> Set[str]:
    with open(path) as f:
        return {line.split(':')[1].split('$')[2] for line in f.read().split('\n') if
                ':' in line and not any(c in line for c in '!*')}


def generate_all_words(possible_chars: str, min_size: int, max_size: int) -> Generator:
    for size in range(min_size, max_size + 1):
        for combination in product(*[possible_chars for _ in range(size)]):
            yield ''.join(combination)


def get_batch_from_generator(generator: Generator, batch_size: int) -> Iterable[int]:
    return []


def find_hash_original(algorithm, words: Iterable, targets, start) -> Set[str]:
    breaked = set()
    for i, tried_password in enumerate(words):
        hashed_tried_password = algorithm(str.encode(tried_password)).hexdigest()
        if hashed_tried_password in targets:
            print(f"{tried_password} découvert au bout de {round(time() - start, 2)} secondes à la {i}ème itération")
            targets.remove(hashed_tried_password)
            breaked.add(tried_password)
            if len(targets) == 0:
                print("Tout les mots de passes ont été découverts")
                break
    return breaked


def build_hash_breaker_process(word_generator, batch_size, start):
    return Process(
        target=find_hash_original,
        args=(
            hashlib.md5,
            {next(word_generator) for _ in range(batch_size)},
            read_shadow('shadow'),
            start
        )
    )


def main():
    chars = ascii_lowercase
    mini, maxi = 6, 6
    possible_combination_number = sum(len(chars) ** i for i in range(mini, maxi + 1))
    print(possible_combination_number / 10 ** 6, "millions de combinaisons possibles")
    word_generator = (word for word in generate_all_words(chars, mini, maxi))
    # batch_size = 3
    batch_size = 1_000_000
    # find_hash_original(
    #     hashlib.md5,
    #     (next(word_generator) for _ in range(batch_size)),
    #     read_shadow('shadow'),
    #     batch_size
    # )
    start = time()
    while True:
        try:
            processes = [build_hash_breaker_process(word_generator, batch_size, start) for _ in range(7)]
            for process in processes:
                process.start()
            for process in processes:
                process.join()
        except StopIteration:
            break
        except KeyboardInterrupt:
            exit(0)


if __name__ == '__main__':
    main()
