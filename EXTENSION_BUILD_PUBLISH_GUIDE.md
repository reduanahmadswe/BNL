# BNL Extension Build + Publish Guide

এই গাইড follow করলে তুমি `BNL Language Support` extension build করে `.vsix` আকারে share করতে পারবে, আর VS Code Marketplace এ publish করতেও পারবে।

## 1) Prerequisites

- Node.js install করা থাকতে হবে
- VS Code install করা থাকতে হবে
- npm কাজ করতে হবে

Check:

```bash
node -v
npm -v
```

## 2) Extension folder

Main extension folder:

- [bnl-language-support](bnl-language-support)

Important files:

- [bnl-language-support/package.json](bnl-language-support/package.json)
- [bnl-language-support/syntaxes/bnl.tmLanguage.json](bnl-language-support/syntaxes/bnl.tmLanguage.json)
- [bnl-language-support/language-configuration/language-configuration.json](bnl-language-support/language-configuration/language-configuration.json)
- [bnl-language-support/README.md](bnl-language-support/README.md)

## 3) Local test in Extension Development Host

- VS Code এ [bnl-language-support](bnl-language-support) folder open করো
- `F5` চাপো
- নতুন VS Code window open হবে
- সেখানে `.bnl` file open করে highlighting test করো

## 4) Build VSIX (installable file)

Terminal:

```bash
cd bnl-language-support
npx @vscode/vsce package
```

Output হবে:

- [bnl-language-support/bnl-language-support-0.1.0.vsix](bnl-language-support/bnl-language-support-0.1.0.vsix)

## 5) Install VSIX locally (any machine)

Option A (command):

```bash
code --install-extension bnl-language-support-0.1.0.vsix --force
```

Option B (UI):

- VS Code Extensions panel
- `...` menu
- **Install from VSIX...**
- VSIX file select করো

## 6) Publish to VS Code Marketplace

### 6.1 Create publisher

- Go: https://marketplace.visualstudio.com/manage
- Create a publisher (example: `reduan`)

### 6.2 Create Azure DevOps PAT

PAT needs marketplace publish permissions.

### 6.3 Login with vsce

```bash
npx @vscode/vsce login reduanahmadswe
```

### 6.4 Update manifest before publish

Edit [bnl-language-support/package.json](bnl-language-support/package.json):

- `publisher` = `reduanahmadswe` (already set)
- `repository.url` = তোমার GitHub repo
- `version` bump করো (`0.1.0` -> `0.1.1`)

### 6.5 Publish

```bash
npx @vscode/vsce publish
```

Patch version auto bump চাইলে:

```bash
npx @vscode/vsce publish patch
```

Alternative (npm scripts):

```bash
npm run publish
npm run publish:patch
npm run publish:minor
npm run publish:major
```

## 7) Release checklist

- [ ] `.bnl` syntax highlighting ঠিক আছে
- [ ] new keywords যোগ হলে grammar updated
- [ ] `README.md` updated
- [ ] version bump করা হয়েছে
- [ ] `publisher` ঠিক আছে
- [ ] VSIX test install pass

## 8) Useful versioning rule

- `patch`: ছোট fix (`0.1.0` -> `0.1.1`)
- `minor`: নতুন feature (`0.1.0` -> `0.2.0`)
- `major`: breaking change (`0.1.0` -> `1.0.0`)
