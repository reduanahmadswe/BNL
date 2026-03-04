const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

function quoteArg(value) {
  return `"${String(value).replace(/"/g, '\\"')}"`;
}

function resolveInterpreterPath(context) {
  const bundledPath = path.join(context.extensionPath, 'runtime', 'interpreter.py');
  if (fs.existsSync(bundledPath)) {
    return bundledPath;
  }

  const workspaceFolders = vscode.workspace.workspaceFolders || [];
  for (const folder of workspaceFolders) {
    const workspacePath = path.join(folder.uri.fsPath, 'bnl-core', 'interpreter.py');
    if (fs.existsSync(workspacePath)) {
      return workspacePath;
    }
  }

  return undefined;
}

async function runBnlFile(context) {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    vscode.window.showErrorMessage('No active editor found. Open a .bnl file first.');
    return;
  }

  const document = editor.document;
  if (document.languageId !== 'bnl' && !document.fileName.toLowerCase().endsWith('.bnl')) {
    vscode.window.showErrorMessage('Active file is not a .bnl file.');
    return;
  }

  await document.save();

  const interpreterPath = resolveInterpreterPath(context);
  if (!interpreterPath) {
    vscode.window.showErrorMessage('BNL interpreter not found. Ensure runtime/interpreter.py exists in extension package.');
    return;
  }

  const config = vscode.workspace.getConfiguration('bnl');
  const pythonPath = config.get('pythonPath', 'python');

  const command = `${quoteArg(pythonPath)} ${quoteArg(interpreterPath)} ${quoteArg(document.fileName)}`;

  const terminal = vscode.window.createTerminal('BNL Runner');
  terminal.show(true);
  terminal.sendText(command);
}

function activate(context) {
  const disposable = vscode.commands.registerCommand('bnl.runFile', () => runBnlFile(context));
  context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = {
  activate,
  deactivate,
};
