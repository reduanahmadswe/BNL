# Banglish Educational Language (Python)

এটা একটি beginner-friendly programming language যেখানে command গুলো Bangla-style কিন্তু English letters এ লেখা।

## Banglish keywords

- variable create: `dorlam`
- print: `dekhao`
- while loop: `guraw`
- end block: `shesh`
- add: `jog`
- subtract: `biyog`
- multiply: `gun`
- divide: `vag`

## Files

- `interpreter.py` -> Banglish interpreter
- `program.bnl` -> sample Banglish program
- `test.bnl` -> extra test program
- `run_program.ps1` -> one command runner

## Run

```bash
python interpreter.py program.bnl
```

PowerShell shortcut:

```powershell
./run_program.ps1
```

## Example program

```text
dorlam x 10
dorlam y 20

dekhao x jog y

dorlam i 0
guraw i < 5
dekhao i
dorlam i i jog 1
shesh
```

## Step-by-step interpreter explanation

### 1) Tokenizer
`ExprParser._tokenize()` expression থেকে token বানায় (number, string, operator, variable)।
`jog`, `biyog`, `gun`, `vag` দেখলে এগুলোকে operator symbol (`+`, `-`, `*`, `/`) এ convert করে।

### 2) Expression parser
Parser precedence মেনে parse করে:
- আগে `*`, `/`
- তারপর `+`, `-`
- শেষে comparison (`<`, `>`, `==`, `!=`, ...)

### 3) Statement parser
`ProgramParser` line by line পড়ে:
- `dorlam name expression`
- `dekhao expression`
- `guraw condition ... shesh`

### 4) Runtime
`Interpreter.execute()`:
- variable set করে
- print করে
- while condition true থাকা পর্যন্ত loop body run করে

### 5) Easy extension
নতুন keyword add করতে parser block-এ নতুন condition যোগ করলেই হবে।
নতুন math শব্দ add করতে `BANG_OP_TO_SYMBOL` map update করলেই হবে।

## Extra test program example

```text
dorlam a 8
dorlam b 2

dekhao a jog b
dekhao a biyog b
dekhao a gun b
dekhao a vag b
```
