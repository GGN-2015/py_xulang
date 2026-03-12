# Xulang
Xulang: an ultra-minimalist programming language with zero memorization of syntax required.

## Introduction
Zhizhi is a lovely mouse-musume. Since she dislikes memorizing grammar rules, Miaomiao designed a programming language for her that requires almost no grammar memorization. If you want to learn how to write Xulang code, See [https://github.com/GGN-2015/py_xulang/blob/main/document/guide.md](https://github.com/GGN-2015/py_xulang/blob/main/document/guide.md).

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

## Program Examples
See `./sample_code/*.xu` on [https://github.com/GGN-2015/py_xulang](https://github.com/GGN-2015/py_xulang).

## Standard Library
See `./xulang/include/Std/*.xu` on [https://github.com/GGN-2015/py_xulang](https://github.com/GGN-2015/py_xulang). It's not necessary to use standard library since most of ther utilities can be easily mannually implemented, they just come as examples.
