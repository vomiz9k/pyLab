#!/usr/bin/python3
import sys
import os
import pickle

upper_alph = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
lower_alph = "abcdefghijklmnopqrstuvwxyz"


def parse_argv():
    data = dict()
    data["mode"] = sys.argv[1]
    for i in range(2, len(sys.argv)):
        if sys.argv[i][:2] == "--":
            data[sys.argv[i][2:]] = sys.argv[i + 1]
            i += 1
    return data


def get_data(args):
    data = str()
    if "input-file" in args.keys():
        file = open(args["input-file"], "r")

        data = file.read()
        file.close()
    else:
        data = sys.stdin.read()
    return data


def put_data(args, data):
    if "output-file" in args.keys():
        file = open(args["output-file"], "w")
        file.write(data)
        file.close()
    else:
        print(data)


def encoded_text(text, key):
    new_text = list()
    for letter in text:
        if letter.isupper():
            new_text.append(upper_alph[(upper_alph.find(letter) + key) % 26])
        elif letter.islower():
            new_text.append(lower_alph[(lower_alph.find(letter) + key) % 26])
        else:
            new_text.append(letter)
    return "".join(new_text)


def encode(args):
    if args["cipher"] == "caesar":
        data = get_data(args)
        key = int(args["key"]) % 26
        encoded = encoded_text(data, key)
        put_data(args, encoded)


def decode(args):
    if args["cipher"] == "caesar":
        data = get_data(args)
        key = (26 - int(args["key"])) % 26
        encoded = encoded_text(data, key)
        put_data(args, encoded)


def train(args):
    data = get_data(args)
    new_values = dict()
    new_values["count"] = 0
    for char in lower_alph:
        new_values[char] = 0

    with open(args["model-file"], "rb") as model_file:
        values = dict()
        try:
            values = pickle.load(model_file)
            for index in values:
                new_values[index] += int(values[index])
        except EOFError:
            print("err")
            pass

    for letter in data:
        if letter.isalpha():
            new_values["count"] += 1
            new_values[letter.lower()] += 1

    with open(args["model-file"], "wb") as model_file:
        pickle.dump(new_values, model_file)


def hack(args):
    data = get_data(args)

    with open(args["model-file"], "rb") as model_file:
        values = pickle.load(model_file)

    model_frequency = get_frequency(values)
    best_diff = 33333.0
    best_key = 0

    for k in range(26):
        curr_values = dict()
        curr_values["count"] = 0
        for char in lower_alph:
            curr_values[char] = 0

        new_data = encoded_text(data, k)
        for char in new_data:
            if char.isalpha():
                curr_values[char.lower()] += 1
                curr_values["count"] += 1

        curr_frequency = get_frequency(curr_values)
        curr_diff = 0.0

        for letter in model_frequency:
            curr_diff += (model_frequency[letter] - curr_frequency[letter]) ** 2

        if curr_diff < best_diff:
            best_diff = curr_diff
            best_key = k

    put_data(args, encoded_text(data, best_key))


def get_frequency(values):
    frequency = dict()
    for key in values:
        if key == "count":
            continue
        frequency[key] = values[key] / values["count"]
    return frequency

    # main:
    print(new_values)


args = parse_argv()

if args["mode"] == "encode":
    encode(args)
elif args["mode"] == "decode":
    decode(args)
elif args["mode"] == "train":
    train(args)
elif args["mode"] == "hack":
    hack(args)
else:
    print("INCORRECT MODE")
