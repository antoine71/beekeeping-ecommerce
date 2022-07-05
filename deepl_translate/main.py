import argparse

import deepl

DEEPL_AUTH_KEY = "d7a8446b-6e1b-34ed-1299-1e5590527586:fx"

parser = argparse.ArgumentParser(description="Translate a file into several languages")
parser.add_argument(
    "-f",
    "--file",
    type=str,
    default="test.md",
    help="Path to the source file you want to translate\
    (default: test.md)",
)
parser.add_argument(
    "-l",
    "--language",
    type=str,
    default="en-gb de",
    nargs="+",
    help="Language you want to translate to (default: en-gb de). You can specify several languages",
)

args = parser.parse_args()


translator = deepl.Translator(DEEPL_AUTH_KEY)

filepath = args.file
filename = filepath.split('/')[-1]
filedir = '/'.join(filepath.split('/')[:-1])

languages = args.language

with open(filepath) as f:
    text = f.read()

for lang in languages:
    result = translator.translate_text(text, target_lang=lang)

    lang_filename = f"{lang[:2]}_{filename[3:]}"
    lang_filepath = '/'.join([filedir, lang_filename])

    try:
        with open(lang_filepath, "x") as f:
            f.write(str(result))
    except FileExistsError:
        with open(lang_filepath, "w") as f:
            f.write(str(result))
