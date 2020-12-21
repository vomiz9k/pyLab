#!/usr/bin/python3
import sys
import os
import pickle

upper_alph = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
lower_alph = 'abcdefghijklmnopqrstuvwxyz'


def encoded_caesar(text, key):
    new_text = list()
    for letter in text:
        if letter.isupper():
            new_text.append(upper_alph[(upper_alph.find(letter) + key) % 26])
        elif letter.islower():
            new_text.append(lower_alph[(lower_alph.find(letter) + key) % 26])
        else:
            new_text.append(letter)
    return ''.join(new_text)


vigenere_table = dict()

for i in range(len(lower_alph)):
    vigenere_table[lower_alph[i]] = dict()
    curr_alph = encoded_caesar(lower_alph, i)
    for j in range(len(lower_alph)):
        vigenere_table[lower_alph[i]][lower_alph[j]] = curr_alph[j]


def in_out_decorator(func):
    def wrapped(args):

        encoded = func(args)
        put_data(args, encoded)
        return encoded
    return wrapped


def parse_argv():
    data = dict()
    data['mode'] = sys.argv[1]
    for i in range(2, len(sys.argv)):
        if sys.argv[i][:2] == '--':
            data[sys.argv[i][2:]] = sys.argv[i + 1]
            i += 1
    return data


def get_data(args):
    data = str()
    if 'input-file' in args.keys():
        with open(args['input-file'], 'r') as file:
            data = file.read()
    if "input-file" in args.keys():
        file = open(args["input-file"], "r")
        data = file.read()
        file.close()
    else:
        data = sys.stdin.read()
    return data


def put_data(args, data):
    if 'output-file' in args.keys():
        with open(args['output-file'], 'w') as file:
            file.write(data)
    else:
        print(data)


def encoded_vigenere(data, keyword):
    key = list()

    for i in range(len(data)):
        key.append(keyword[i % len(keyword)])
    key = ''.join(key)
    encoded = list()

    for i in range(len(data)):
        if data[i].islower():
            encoded.append(vigenere_table[data[i]][key[i]])
        elif data[i].isupper():
            encoded.append(vigenere_table[data[i].lower()][key[i]].upper())
        else:
            encoded.append(data[i])

    return ''.join(encoded)


def decoded_vigenere(data, keyword):
    key = list()

    for i in range(len(data)):
        key.append(keyword[i % len(keyword)])
    key = ''.join(key)
    encoded = list()

    for i in range(len(data)):
        curr_str = vigenere_table[key[i]]
        if data[i].islower():
            for sym in lower_alph:
                if curr_str[sym] == data[i]:
                    encoded.append(sym)
        elif data[i].isupper():
            for sym in lower_alph:
                if curr_str[sym] == data[i].lower():
                    encoded.append(sym.upper())
        else:
            encoded.append(data[i])

    return ''.join(encoded)

    with open(args["model-file"], "rb") as model_file:
        values = dict()
        try:
            values = pickle.load(model_file)
            for index in values:
                new_values[index] += int(values[index])
        except EOFError:
            pass

def hack_by_base(data, args):
    with open(args['base']) as base:
        words = set()
        for line in base:
            words.add(line)

    best_match = 0
    best_key = 0

    for key in range(26):
        curr_match = 0
        curr_data = encoded_caesar(data, key)
        curr_data_list = curr_data.split()
        for el in curr_data_list:
            if el in words:
                curr_match += 1

        if (curr_match > best_match):
            best_match = curr_match
            best_key = key

    return encoded_caesar(data, best_key)


def hack_by_model(data, args):
    with open(args['model-file'], 'rb') as model_file:
        values = pickle.load(model_file)

    model_frequency = get_frequency(values)
    best_diff = 3333210937801733.0  # very big number
    best_key = 0

    for k in range(26):
        curr_values = dict()
        curr_values['count'] = 0
        for char in lower_alph:
            curr_values[char] = 0

        new_data = encoded_caesar(data, k)
        for char in new_data:
            if char.isalpha():
                curr_values[char.lower()] += 1
                curr_values['count'] += 1

        curr_frequency = get_frequency(curr_values)
        curr_diff = 0.0

        for letter in model_frequency:
            curr_diff += (model_frequency[letter] -
                          curr_frequency[letter]) ** 2

        if curr_diff < best_diff:
            best_diff = curr_diff
            best_key = k

    return encoded(data, best_key)


def get_frequency(values):
    frequency = dict()
    for key in values:
        if key == 'count':
            continue
        frequency[key] = values[key] / values['count']
    return frequency


def encode(args):
    data = get_data(args)
    if args['cipher'] == 'caesar':
        key = int(args['key']) % 26
        encoded = encoded_caesar(data, key)
    elif args['cipher'] == 'vigenere':
        keyword = args['key']
        encoded = encoded_vigenere(data, keyword)
    put_data(encoded)


def decode(args):
    data = get_data(args)
    if args['cipher'] == 'caesar':
        key = (26 - int(args['key'])) % 26
        decoded = encoded_caesar(data, key)
    elif args['cipher'] == 'vigenere':
        keyword = args['key']
        decoded = decoded_vigenere(data, keyword)
    put_data(decoded)


def train(args):
    data = get_data(args)
    new_values = dict()
    new_values['count'] = 0
    for char in lower_alph:
        new_values[char] = 0

    with open(args['model-file'], 'rb') as model_file:
        try:
            values = dict()
            values = pickle.load(model_file)
            for index in values:
                new_values[index] += int(values[index])
        except EOFError:
            pass

    for letter in data:
        if letter.isalpha():
            new_values['count'] += 1
            new_values[letter.lower()] += 1

    with open(args['model-file'], 'wb') as model_file:
        pickle.dump(new_values, model_file)


def hack(args):
    data = get_data(args)
    if 'base' in args.keys:  # --base base.txt means base.txt is file with big amount of words. check words.txt
        encoded = hack_by_base(data, args)
    elif 'model-file' in args.keys:
        encoded = hack_by_model(data, args)
    else:
        print('ERROR! Need something to hack. Try --base or --model-file.')

    put_data(encoded)


# main:
args = parse_argv()

if args['mode'] == 'encode':
    encode(args)
elif args['mode'] == 'decode':
    decode(args)
elif args['mode'] == 'train':
    train(args)
elif args['mode'] == 'hack':
    hack(args)
else:
    print('INCORRECT MODE')
