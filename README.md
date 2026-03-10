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
python3 -m xulang -I <include_path> <filepath.xu>
```

## Lexical Units
Constants: Character strings consisting of letters, digits, and underscores, starting with a digit or uppercase letter. Examples: `123`, `ABX_1`, `T`, etc.

Variables: Character strings consisting of letters, digits, and underscores, starting with a lowercase letter or underscore. Examples: `a`, `_name`, `_var1`.

String Matching: A string starting with an asterisk immediately followed by a variable name. Examples: `*a`, `*_x`, `*v1`.

## Program Examples
```
// Define IF ternary operator (with short-circuit evaluation)
(IF TRUE  a b) => a
(IF FALSE a b) => b

// Define MERGE: merge any two sequences
(MERGE (*a) (*b)) => (*a *b)

// Define HEAD: get the first element of a non-empty sequence
(HEAD (a *b)) => a

// Define REV: reverse any sequence
(REV ()) => ()
(REV (a *b)) => (MERGE (REV (*b)) (a))

// Define TAIL: get the last element of a non-empty sequence
(TAIL (*a)) => (HEAD (REV (*a)))

// Run program (result is E)
(IF FALSE X (TAIL (A B C D E)))

// Run program (result is 1)
(IF TRUE 1 (TAIL (A B C D E)))
```
