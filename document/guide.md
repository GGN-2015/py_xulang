# How to write Xulang code?

> [!NOTE]
> This tutorial is under construction. Stay tuned, and contributions are welcome.

Xulang (pronunciation: **/ʃjuː lɑːŋ/**) is an extremely minimalist interpreted language that runs via an interpreter. Without plugins, the language accepts no user input; all programs and data are from Xulang source code files. After execution, Xulang outputs the computation results to standard output.

In Xulang's programming world, there are no variables and no functions. Everything is implemented through symbols, pattern matching, and substitution.

In Xulang, the following parts are particularly important for programming:
1. Xulang basic syntax;
2. Xulang preprocessor commands;
3. Xulang standard library;

Even if you know nothing about Xulang's preprocessor commands and standard library, you can still use Xulang to write any algorithm you want to implement -- though the code may be somewhat verbose or complex, which means Xulang is a programming language that requires little memorization of syntax rules or library usage.

To learn more about preprocessor commands, see [./preprocessor.md](./preprocessor.md).

To learn how to use Xulang standard library, see [./std.md](./std.mds).

## Xulang Syntax

### Symbols

Before we introduce the syntax of Xulang, we first present the following three fundamental concepts: constant symbols, match symbols, and sequence match symbols.

A **constant symbol** starts with an uppercase letter or a digit, and may contain lowercase letters, uppercase letters, underscores, dots, and digits. Constant symbols are typically used to represent data in programs. For example, `A.2`, `25`, and `12A` are all valid constant symbols. In a matching statement, a constant symbol can only match **itself**.

A **match symbol** starts with a lowercase letter or an underscore, and may contain lowercase letters, uppercase letters, underscores, dots, and digits. In a matching statement, one match symbol can match one expression or constant symbol. For example, `a.2`, `_25`, and `_name` are all valid match symbols.

A **sequence match symbol** starts with an asterisk `*`, followed immediately by a variable name that is valid as a match symbol. In a matching statement, a sequence match symbol can match zero or any number of expressions or constant symbols.

### Substitution Rules

In Xulang, substitution rules generally take the following form:

```
<Pattern> => <Result>
```

The core of the Xulang programming language is to define a series of substitution rules. When multiple rules match simultaneously, the rule defined earlier takes precedence.

The `<Pattern>` part must be a sequence of symbols. In matching rules, parentheses can only match parentheses.

In `<Result>`, you can use the match sybmols defined in `<Pattern>` to use its match value. 

#### Get First Element in List

Try this sample in Xulang interpretor:
```
// define three match rules, where "Head" is a constant symbol.
(Head ()) => 
(Head (a)) => a
(Head (a *b)) => a

// line without "=>" means calculate and output its answer
(Head (A B C D E))
```

The program will output a single "A" symbol, and the expression begins with "Head" then can be used to calculate the first symol in a sequence (enclosed in parentheses).

During the evaluation of `(Head (A B C D E))`, the pattern `(Head ())` fails to match because `)` cannot match the symbol `A`. Similarly, `(Head (A B C D E))` does not match `(Head (a))`, since the symbol `a` can match at most one symbol, while the sequence `(A B C D E)` contains five symbols.

Finally, `(Head (A B C D E))` successfully matches `(Head (a *b))`, where `a` matches `A` and `*b` matches `B C D E`. According to the `<Result>` of the current matching rule, we take the value matched by `a` as the final result.

> [!IMPORTANT]
> Note that to avoid ambiguous matches, Xulang syntax requires that sequence match symbols must appear at the end of a parenthesized expression.

#### Merge two List

Try this sample in Xulang interpretor:
```
(Merge (*a) (*b)) => (*a *b)

// calculate expression
(Merge (A B C) (D E F))
```

The program will output `(A B C D E F)` which is the merged list of `(A B C)` and `(D E F)`.

During the matching process, `(Merge (A B C) (D E F))` successfully matches the pattern `(Merge (*a) (*b))`, where `*a` matches the sequence `A B C` and `*b` matches the sequence `D E F`. In the result `(*a *b)`, the matched results of `*a` and `*b` are expanded and substituted into the result expression.

#### Reverse a List

Try this sample in Xulang interpretor:
```
// rules
(Merge (*a) (*b)) => (*a *b)
(Rev ()) => ()
(Rev (a)) => (a)
(Rev (a *b)) => (Merge (Rev (*b)) (a))

// expression
(Rev (A B C D E))
```

After execution the program will output `(E D C B A)`. The computation process is listed as follows:

1. `(Rev (A B C D E))`
2. `(Merge (Rev (B C D E)) (A))`
3. `(Merge (Merge (Rev (C D E)) (B)) (A))`
4. `(Merge (Merge (Merge (Rev (D E)) (C)) (B)) (A))`
5. `(Merge (Merge (Merge (Merge (Rev (E)) (D)) (C)) (B)) (A))`
6. `(Merge (Merge (Merge (Merge (E) (D)) (C)) (B)) (A))`
7. `(Merge (Merge (Merge (E D) (C)) (B)) (A))`
8. `(Merge (Merge (E D C) (B)) (A))`
9. `(Merge (E D C B) (A))`
10. `(E D C B A)`

If you are curious about the substitution process, use `python3 -m xulang --verbose` to see every step.

Although this execution process appears to be a recursive function, it is essentially just the result of multiple matches and substitutions.

> [!IMPORTANT]
> Under normal circumstances, when there are multiple levels of nested parentheses, we always attempt to match the **inner parentheses first**. Matching on the outer parentheses is only attempted when no further matches can be made in the inner parentheses.

For example, at the stage of `(Merge (Rev (B C D E)) (A))`, this expression could match `(Merge (*a) (*b))` as follows: `*a` matches `Rev (B C D E)` (note that `(B C D E)` is treated as a single element at this point, and `Rev` is regarded as a constant symbol), while `*b` matches `A`. However, since the matching of the inner expression `(Rev (B C D E))` has not yet completed, the match against `(Merge (*a) (*b))` will not be performed.

#### Summary

In Xulang's matching rules, parentheses can only match parentheses. If no parentheses are written in the pattern, a match symbol itself can match either a parenthesized expression or a constant symbol. When an expression contains nested parentheses, inner matches are evaluated first if available; only when no inner match exists will an attempt be made to match the outer parentheses. When multiple matching rules are applicable, the rule defined earlier takes precedence. Later rules are only tried if the earlier ones fail to match.

### Line Escape

#### Line Merge

Since one substitution rule can only lies in one line, its very hard to program or read a very complex expression. When faced with this problem, you can add a back-slash `\` at the end of line to combine two adjacent lines.

The following is a program to check which list is longer.
```
(WhichIsLonger () ()) => SameLength
(WhichIsLonger () (*a)) => List2
(WhichIsLonger (*a) ()) => List1
(WhichIsLonger (a0 *a1) (b0 *b1)) => \
    (WhichIsLonger (*a1) (*b1))

(WhichIsLonger (A B) (C))
(WhichIsLonger (A) (B C))
(WhichIsLonger (A B) (B C))
```

Which will output three line of content:
```
List1
List2
SameLength
```

#### Line Split

If you want to write mutiple substitution rule in one line, try use `\n` to seperate them.

```
(MatchA A) => TRUE \n (MatchA a) => FALSE

(MatchA A)
(MatchA B)
```

Which will output two line of content
```
TRUE
FALSE
```

Since `(MatchA A) => TRUE` is infront of `(MatchA a) => FALSE`, when both of the pattern matched, the first one will be in priority.
