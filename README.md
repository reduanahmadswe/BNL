# Banglish Educational Language (Python)

এটা একটি beginner-friendly programming language যেখানে command গুলো Bangla-style কিন্তু English letters এ লেখা।

## Banglish keywords

- variable create: `dorlam`
- print: `dekhao`
- input: `naw`
- if: `jodi`
- else: `nahole`
- while loop: `guraw`
- end block: `shesh`
- break: `bhenge_jao`
- continue: `cholte_thako`
- add: `jog`
- subtract: `biyog`
- multiply: `gun`
- divide: `vag`
- logical and/or/not: `ar`, `ba`, `na`
- boolean literals: `shotti`, `mitha`

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

naw age "tumar boyosh dao: "
dekhao age
dekhao "boyosh:" age

dorlam i 0
guraw i < 5
dekhao i
dorlam i i jog 1
shesh

jodi x > 5
dekhao "x boro"
nahole
dekhao "x choto"
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
- `dekhao "text" variable` (multiple value print)
- `naw name [prompt]`
- `jodi condition ... nahole ... shesh`
- `guraw condition ... shesh`
- `bhenge_jao`, `cholte_thako`

### 4) Runtime
`Interpreter.execute()`:
- variable set করে
- print করে
- `naw` এ user input নেয়
- `jodi/nahole` condition চালায়
- while condition true থাকা পর্যন্ত loop body run করে
- `bhenge_jao` loop break করে
- `cholte_thako` next loop iteration এ যায়

### 5) Easy extension
নতুন keyword add করতে parser block-এ নতুন condition যোগ করলেই হবে।
নতুন math শব্দ add করতে `BANG_OP_TO_SYMBOL` map update করলেই হবে।

## Extra test program example

```text
dorlam a 8
dorlam b 2

naw name "tomar nam dao: "
dekhao name

dekhao a jog b
dekhao a biyog b
dekhao a gun b
dekhao a vag b
```

## Practice problems (with solutions)

নিচে কয়েকটা basic problem আর ready solution দেওয়া আছে। এগুলো copy করে `.bnl` file এ run করতে পারো।

### Problem 1: Jog (Addition)
দুটি সংখ্যা `a` এবং `b` যোগ করে print করো।

**Solution:**

```text
dorlam a 12
dorlam b 8
dekhao "jogfol:" a jog b
```

### Problem 2: Biyog (Subtraction)
দুটি সংখ্যা `x` এবং `y` এর পার্থক্য print করো।

**Solution:**

```text
dorlam x 20
dorlam y 7
dekhao "biyogfol:" x biyog y
```

### Problem 3: Input + Print
user এর নাম input নিয়ে greeting print করো।

**Solution:**

```text
naw nam "tomar nam dao: "
dekhao "hello" nam
```

### Problem 4: If/Else condition
input age 18 বা তার বেশি হলে `adult`, না হলে `not adult` print করো।

**Solution:**

```text
naw age "boyosh dao: "
jodi age >= 18
dekhao "adult"
nahole
dekhao "not adult"
shesh
```

### Problem 5: Loop (1 থেকে 5 print)
loop দিয়ে 1 থেকে 5 পর্যন্ত print করো।

**Solution:**

```text
dorlam i 1
guraw i <= 5
dekhao i
dorlam i i jog 1
shesh
```

### Problem 6: Even number skip (continue) + break demo
1 থেকে 10 এর মধ্যে odd number print করো, আর `7` এ এসে loop বন্ধ করো।

**Solution:**

```text
dorlam i 1
guraw i <= 10

jodi i == 7
bhenge_jao
shesh

jodi i == 2 ba i == 4 ba i == 6
dorlam i i jog 1
cholte_thako
shesh

dekhao i
dorlam i i jog 1
shesh
```
