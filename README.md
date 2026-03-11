# xulang
xulang: an ultra-minimalist programming language with zero memorization of grammar required.

## Introduction
Zhizhi is a lovely mouse-musume. Since she dislikes memorizing grammar rules, Miaomiao designed a programming language for her that requires almost no grammar memorization.

## Install
```bash
pip install xulang
```

## Usage
```bash
# xulang interactive CLI
python3 -m xulang

# run file
python3 -m xulang <filepath.xu>

# run file with include_path
python3 -m xulang -I <include_path>

# use --verbose to see matching process
python3 -m xulang --verbose
```

## Lexical Units
Constants: Character strings consisting of letters, digits, and underscores, starting with a digit or uppercase letter. Examples: `123`, `ABX_1`, `T`, etc.

Variables: Character strings consisting of letters, digits, and underscores, starting with a lowercase letter or underscore. Examples: `a`, `_name`, `_var1`.

List Matching: A string starting with an asterisk immediately followed by a variable name. Examples: `*a`, `*_x`, `*v1`.

## Program Examples
See `./sample_code/*.xu` on [https://github.com/GGN-2015/py_xulang](https://github.com/GGN-2015/py_xulang).

## Standard Library
See `./xulang/include/Std/*.xu` on [https://github.com/GGN-2015/py_xulang](https://github.com/GGN-2015/py_xulang). It's not necessary to use standard library since most of ther utilities can be easily mannually implemented, they just come as examples.
