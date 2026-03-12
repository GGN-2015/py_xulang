# How to write Xulang code?

> [!NOTE]
> This tutorial is being continuously updated. Stay tuned, and contributions are welcome.

Xulang is an extremely minimalist interpreted language that runs via an interpreter. Without plugins, the language accepts no user input; all programs and data are from Xulang source code files. After execution, Xulang outputs the computation results to standard output.

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

The `<Pattern>` part must be a sequence of symbols . In matching rules, parentheses can only match parentheses.

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

Note that to avoid ambiguous matches, Xulang syntax requires that sequence match symbols must appear at the end of a parenthesized expression.

#### Reverse a List
