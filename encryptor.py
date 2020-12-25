#!/usr/bin/python3
import sys
import os
import pickle
import argparse
from abc import ABC, abstractmethod
from string import ascii_uppercase as upper_alph
from string import ascii_lowercase as lower_alph


def parse_argv():
    parser = argparse.ArgumentParser(description='Working with some cifers.')
    parser.add_argument('--input-file', action='store',
                        type=argparse.FileType('r'), required=False, help='input file')
    parser.add_argument('--output-file', action='store',
                        type=argparse.FileType('w'), required=False, help='output file')

    subparsers = parser.add_subparsers(title='mode', dest='mode', help='mode')

    encoder = subparsers.add_parser('encode', help='encode')
    encoder.add_argument('--key', action='store',
                         type=str, required=True, help='key')
    encoder.add_argument('--cipher', action='store',
                         type=str, required=True, help='cipher')

    decoder = subparsers.add_parser('decode', help='decode')
    decoder.add_argument('--key', action='store',
                         type=str, required=True, help='key')
    decoder.add_argument('--cipher', action='store',
                         type=str, required=True, help='cipher')

    trainer = subparsers.add_parser('train', help='train')
    trainer.add_argument('--model-file', action='store',
                         type=str, required=True, help='model file')
    trainer.add_argument('--cipher', action='store',
                         type=str, required=True, help='cipher')

    hacker = subparsers.add_parser('hack', help='hack')
    hacker.add_argument('--cipher', action='store',
                        type=str, required=True, help='cipher')

    subhackparsers = hacker.add_subparsers(
        title='method', dest='method', help='hacking method')

    base_hacker = subhackparsers.add_parser(
        'base', help='hacking by base file')
    base_hacker.add_argument('--base-file', action='store',
                             type=argparse.FileType('r'), required=True, help='base file')

    model_hacker = subhackparsers.add_parser(
        'model', help='hacking by model file')
    model_hacker.add_argument('--model-file', action='store',
                              type=argparse.FileType('rb'), required=True, help='model file')

    return parser.parse_args()


def get_data(input_file):
    data = str()
    if input_file is None:
        data = sys.stdin.read()
    else:
        data = input_file.read()
    return data


def put_data(data, output_file):
    if output_file is None:
        sys.stdout.write(data)
    else:
        output_file.write(data)


def get_frequency(freq):
    frequency = dict()
    count = sum(freq.values())
    for key in freq:
        frequency[key] = freq[key] / count
    return frequency


class cipher(ABC):

    @abstractmethod
    def encrypt(self, text, key):
        pass

    @abstractmethod
    def decrypt(self, text, key):
        pass


class caesar(cipher):
    def encrypt(self, text, key):
        new_text = []
        for letter in text:
            if letter.isupper():
                new_text.append(
                    upper_alph[(upper_alph.find(letter) + key) % len(lower_alph)])
            elif letter.islower():
                new_text.append(
                    lower_alph[(lower_alph.find(letter) + key) % len(lower_alph)])
            else:
                new_text.append(letter)
        return ''.join(new_text)

    def decrypt(self, text, key):
        return self.encrypt(text, (len(lower_alph) - key) % len(lower_alph))

    def train(self, data, model_file):
        new_values = dict()
        for char in lower_alph:
            new_values[char] = 0

        try:
            with open(model_file, 'rb') as file:
                values = dict()
                values = pickle.load(file)
                for index in values:
                    new_values[index] += int(values[index])
        except EOFError:
            pass
        except FileNotFoundError:
            pass

        for letter in data:
            if letter.isalpha():
                new_values[letter.lower()] += 1

        with open(model_file, 'wb') as file:
            pickle.dump(new_values, file)

    def hack(self, method, data, needed_file):
        if(method == 'base'):
            return self.hack_by_base(data, needed_file)
        elif (method == 'model'):
            return self.hack_by_model(data, needed_file)
        else:
            raise NameError

    def hack_by_base(self, data, base_file):
        words = set()
        for line in base_file:
            words.add(line[:-1])

        best_match = 0
        best_key = 0

        for key in range(len(lower_alph)):
            curr_match = 0
            curr_data = self.encrypt(data, key)
            curr_data_list = curr_data.split()
            for el in curr_data_list:
                if el in words:
                    curr_match += 1

            if (curr_match > best_match):
                best_match = curr_match
                best_key = key

        return self.encrypt(data, best_key)

    def hack_by_model(self, data, model_file):
        values = pickle.load(model_file)

        model_frequency = get_frequency(values)
        best_diff = float('inf')
        best_key = 0

        for key in range(len(lower_alph)):
            curr_values = dict()
            for char in lower_alph:
                curr_values[char] = 0

            new_data = self.encrypt(data, key)
            for char in new_data:
                if char.isalpha():
                    curr_values[char.lower()] += 1

            curr_frequency = get_frequency(curr_values)
            curr_diff = 0.0

            for letter in model_frequency:
                curr_diff += (model_frequency[letter] -
                              curr_frequency[letter]) ** 2

            if curr_diff < best_diff:
                best_diff = curr_diff
                best_key = key

        return self.encrypt(data, best_key)


vigenere_table = dict()
for i in range(len(lower_alph)):
    vigenere_table[lower_alph[i]] = dict()
    curr_alph = caesar().encrypt(lower_alph, i)
    for j in range(len(lower_alph)):
        vigenere_table[lower_alph[i]][lower_alph[j]
                                      ] = lower_alph[(i + j) % len(lower_alph)]


class vigenere(cipher):

    def encrypt(self, text, key):
        encoded = []

        for i in range(len(text)):
            if text[i].islower():
                encoded.append(vigenere_table[text[i]][key[i % len(key)]])
            elif text[i].isupper():
                encoded.append(
                    vigenere_table[text[i].lower()][key[i % len(key)]].upper())
            else:
                encoded.append(text[i])

        return ''.join(encoded)

    def decrypt(self, text, key):
        encoded = []

        for i in range(len(text)):
            curr_str = vigenere_table[key[i % len(key)]]
            if text[i].islower():
                for sym in lower_alph:
                    if curr_str[sym] == text[i]:
                        encoded.append(sym)
            elif text[i].isupper():
                for sym in lower_alph:
                    if curr_str[sym] == text[i].lower():
                        encoded.append(sym.upper())
            else:
                encoded.append(text[i])

        return ''.join(encoded)


def encode(cipher, key, input_file, output_file):
    data = get_data(input_file)
    if cipher == 'caesar':
        encoded = caesar().encrypt(data, int(key))
    elif cipher == 'vigenere':
        encoded = vigenere().encrypt(data, key)

    put_data(encoded, output_file)


def decode(cipher, key, input_file, output_file):
    data = get_data(input_file)
    if cipher == 'caesar':
        decoded = caesar().decrypt(data, int(key))
    elif args.cipher == 'vigenere':
        decoded = vigenere().decrypt(data, key)

    put_data(decoded, output_file)


def hack(cipher, method, input_file, output_file, needed_file):
    if(cipher != 'caesar'):
        raise NameError

    data = get_data(input_file)

    result = caesar().hack(method, data, needed_file)

    put_data(result, output_file)


def train(cipher, input_file, model_file):
    if(cipher != 'caesar'):
        raise NameError

    data = get_data(input_file)
    caesar().train(data, model_file)


# main:
args = parse_argv()

if args.mode == 'encode':
    encode(args.cipher, args.key, args.input_file, args.output_file)
elif args.mode == 'decode':
    decode(args.cipher, args.key, args.input_file, args.output_file)
elif args.mode == 'train':
    train(args.cipher, args.input_file, args.model_file)
elif args.mode == 'hack':
    if(args.method == 'base'):
        hack(args.cipher, args.method, args.input_file,
             args.output_file, args.base_file)
    elif(args.method == 'model'):
        hack(args.cipher, args.method, args.input_file,
             args.output_file, args.model_file)
