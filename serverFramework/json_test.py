import json

from utils import log


def load(path):
    with open(path, 'r', encoding='utf-8') as f:
        s = f.read()
        return s, json.loads(s)


def main():
    s1, s2 = load('User.txt')
    log('s:', s1, s2[0])


if __name__ == "__main__":
    main()
