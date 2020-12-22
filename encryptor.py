#!/usr/bin/python3
import sys
import os
import pickle
import argparse

upper_alph = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
lower_alph = 'abcdefghijklmnopqrstuvwxyz'


def encoded_caesar(text, key):
    new_text = []
    for letter in text:
        if letter.isupper():
            new_text.append(upper_alph[(upper_alph.find(letter) + key) % len(lower_alph)])
        elif letter.islower():
            new_text.append(lower_alph[(lower_alph.find(letter) + key) % len(lower_alph)])
        else:
            new_text.append(letter)
    return ''.join(new_text)


vigenere_table = dict()

for i in range(len(lower_alph)):
    vigenere_table[lower_alph[i]] = dict()
    curr_alph = encoded_caesar(lower_alph, i)
    for j in range(len(lower_alph)):
        vigenere_table[lower_alph[i]][lower_alph[j]] = curr_alph[j]




def parse_argv():
    parser = argparse.ArgumentParser(description='Working with some cifers.')
    parser.add_argument('--input-file', action='store', type=argparse.FileType('r'), required=False, help='input file')
    parser.add_argument('--output-file', action='store', type=argparse.FileType('w'), required=False, help='output file')
    
    subparsers = parser.add_subparsers(title='mode', dest='mode', help='mode')

    encoder = subparsers.add_parser('encode', help='encode')
    encoder.add_argument('--cipher', action='store', type=str, required=True, help='cipher')
    encoder.add_argument('--key', action='store', type=str, required=True, help='key')

    decoder = subparsers.add_parser('decode', help='decode')
    decoder.add_argument('--cipher', action='store', type=str, required=True, help='cipher')
    decoder.add_argument('--key', action='store', type=str, required=True, help='key')
    
    trainer = subparsers.add_parser('train', help='train')
    trainer.add_argument('--model-file', action='store', type=str, required=True, help='model file')

    hacker= subparsers.add_parser('hack', help='hack')
    subhackparsers = hacker.add_subparsers(title='method', dest='method', help='hacking method')

    base_hacker = subhackparsers.add_parser('base', help='hacking by base file')
    base_hacker.add_argument('--base-file', action='store', type=argparse.FileType('r'), required=True, help='base file')

    model_hacker = subhackparsers.add_parser('model', help='hacking by model file')
    model_hacker.add_argument('--model-file', action='store', type=argparse.FileType('rb'), required=True, help='model file')

    
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
        print(data)
    else:
        output_file.write(data)
        


def encoded_vigenere(data, keyword):
    key = []

    for i in range(len(data)):
        key.append(keyword[i % len(keyword)])
    key = ''.join(key)
    encoded = []

    for i in range(len(data)):
        if data[i].islower():
            encoded.append(vigenere_table[data[i]][key[i]])
        elif data[i].isupper():
            encoded.append(vigenere_table[data[i].lower()][key[i]].upper())
        else:
            encoded.append(data[i])

    return ''.join(encoded)


def decoded_vigenere(data, keyword):
    key = []

    for i in range(len(data)):
        key.append(keyword[i % len(keyword)])
    key = ''.join(key)
    encoded = []

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

    

def hack_by_base(input_file, output_file, base_file):
    data = get_data(input_file)
    words = set()
    for line in base_file:
        words.add(line[:-1])

    best_match = 0
    best_key = 0

    for key in range(len(lower_alph)):
        curr_match = 0
        curr_data = encoded_caesar(data, key)
        curr_data_list = curr_data.split()
        print(curr_data_list)
        for el in curr_data_list:
            if el in words:
                curr_match += 1

        if (curr_match > best_match):
            best_match = curr_match
            best_key = key

    put_data(encoded_caesar(data, best_key), output_file)


def hack_by_model(input_file, output_file, model_file):
    data = get_data(input_file)
    values = pickle.load(model_file)

    model_frequency = get_frequency(values)
    best_diff = 3333210937801733.0  # very big number
    best_key = 0

    for k in range(len(lower_alph)):
        curr_values = dict()
        for char in lower_alph:
            curr_values[char] = 0
        

        new_data = encoded_caesar(data, k)
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
            best_key = k

    put_data(encoded_caesar(data, best_key), output_file)


def get_frequency(freq):
    frequency = dict()
    count = sum(freq.values()) 
    for key in values:
        frequency[key] = freq[key] / count
    return frequency


def encode(cipher, key, input_file, output_file):
    data = get_data(input_file)
    if cipher == 'caesar':
        encoded = encoded_caesar(data, int(key))
    elif cipher == 'vigenere':
        encoded = encoded_vigenere(data, key)
    put_data(encoded, output_file)


def decode(cipher, key, input_file, output_file):
    data = get_data(input_file)
    if cipher == 'caesar':
        key = (len(lower_alph) - int(key)) % len(lower_alph)
        decoded = encoded_caesar(data, key)
    elif args.cipher == 'vigenere':
        decoded = decoded_vigenere(data, key)
    put_data(decoded, output_file)


def train(input_file, model_file):
    data = get_data(input_file)
    new_values = dict()
    for char in lower_alph:
        new_values[char] = 0

    with open(model_file, 'rb') as model_file:
        try:
            values = dict()
            values = pickle.load(model_file)
            for index in values:
                new_values[index] += int(values[index])
        except EOFError:
            pass

    for letter in data:
        if letter.isalpha():
            new_values[letter.lower()] += 1

    with open(model_file, 'wb') as model_file:
        pickle.dump(new_values, model_file)



#main:

args = parse_argv()

if args.mode == 'encode':
    encode(args.cipher, args.key, args.input_file, args.output_file)
elif args.mode == 'decode':
    decode(args.cipher, args.key, args.input_file, args.output_file)
elif args.mode == 'train':
    train(args.input_file, args.model_file)
elif args.mode == 'hack':
    if args.method == 'base':
        hack_by_base(args.input_file, args.output_file, args.base_file)
    elif args.method == 'model':
        hack_by_model(args.input_file, args.output_file, args.model_file)
else:
    print('INCORRECT MODE')
