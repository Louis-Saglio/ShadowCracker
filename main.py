import hashlib
from itertools import product
from multiprocessing import Process, cpu_count
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
        for combination in product(possible_chars, repeat=size):
            yield ''.join(combination)


def find_hash_original(algorithm, words: Iterable, targets, start):
    for tried_password in words:
        hashed_tried_password = algorithm(str.encode(tried_password)).hexdigest()
        if hashed_tried_password in targets:
            print(f"{tried_password} découvert au bout de {round(time() - start, 2)} secondes")
            targets.remove(hashed_tried_password)
            with open('found', 'a') as f:
                f.write(f"{tried_password} {time() - start}\n")
            if len(targets) == 0:
                print("Tout les mots de passes ont été découverts")
                break


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
    word_generator = generate_all_words(chars, mini, maxi)
    batch_size = 50_000
    start = time()
    while True:
        try:
            processes = [build_hash_breaker_process(word_generator, batch_size, start) for _ in range(cpu_count())]
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
