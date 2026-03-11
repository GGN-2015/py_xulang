# xulang
xulang: an ultra-minimalist programming language with zero memorization of rules required.

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
See `./sample_code/*.xu` on .

## Standard Libarary