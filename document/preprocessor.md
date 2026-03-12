# Xulang Preprocessor Commands

> [!NOTE]
> This tutorial is under construction. Stay tuned, and contributions are welcome.

Even without Xulang preprocessor commands, you can implement all the algorithmic functionality you need. However, if you want to implement higher-order functions (function templates that take other functions as input), you will need to rely on preprocessor directives.

## `#define` command

The `#define` directive allows users to define macro variables. A macro variable name must be a string starting with a letter or an underscore, consisting of letters, digits, and underscores—this requirement is similar to variable names in many programming languages. `#define` can conveniently substitute a symbol with almost any string, which can later be embedded into both rules and expressions.

### Basic Usage

Try this sample program:
```
#define OPTION_1 Hello
#define OPTION_2 World
#define VAL_1 1
#define VAL_2 2

${OPTION_${VAL_1}} ${OPTION_${VAL_2}}
```

In this sample program, we defined four macro variable `OPTION_1`, `OPTION_2`, `VAL_1` and `VAL_2`. When a variable is defined, you can use `${...}` to expand its value. The expansion process will continue to work until no `${...}` found in the current expression.

The expansion process is listed as follows:
1. `${OPTION_${VAL_1}} ${OPTION_${VAL_2}}`
2. `${OPTION_1} ${OPTION_${VAL_2}}`
3. `Hello ${OPTION_${VAL_2}}`
4. `Hello ${OPTION_2}`
5. `Hello World`

So finally, the program will output `Hello World`.
