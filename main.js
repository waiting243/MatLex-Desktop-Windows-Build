const { app, BrowserWindow, shell, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');

function sendWindowState(win) {
  if (!win || win.isDestroyed()) return;
  win.webContents.send('matlex-window-state', { maximized: win.isMaximized() });
}

function ensureDesktopShortcut() {
  if (process.platform !== 'win32' || !app.isPackaged) return;
  try {
    const desktop = app.getPath('desktop');
    const shortcutPath = path.join(desktop, 'MatLex.lnk');
    const target = process.env.PORTABLE_EXECUTABLE_FILE || process.execPath;
    const details = {
      target,
      cwd: path.dirname(target),
      description: 'MatLex 保研复习',
      icon: target,
      iconIndex: 0,
      appUserModelId: 'com.materialex.desktop'
    };
    const op = fs.existsSync(shortcutPath) ? 'update' : 'create';
    shell.writeShortcutLink(shortcutPath, op, details);
  } catch (err) {
    console.warn('Desktop shortcut creation skipped:', err?.message || err);
  }
}

function createWindow() {
  const win = new BrowserWindow({
    title: 'MatLex',
    width: 1440,
    height: 900,
    minWidth: 980,
    minHeight: 680,
    show: false,
    frame: false,
    backgroundColor: '#f7fbff',
    autoHideMenuBar: true,
    icon: path.join(__dirname, 'build', process.platform === 'win32' ? 'icon.ico' : 'icon.png'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      spellcheck: false
    }
  });

  win.loadFile(path.join(__dirname, 'src', 'index.html'));
  win.once('ready-to-show', () => {
    win.show();
    sendWindowState(win);
  });
  win.on('maximize', () => sendWindowState(win));
  win.on('unmaximize', () => sendWindowState(win));

  win.webContents.setWindowOpenHandler(({ url }) => {
    if (/^https?:/i.test(url)) shell.openExternal(url);
    return { action: 'deny' };
  });
  win.webContents.on('will-navigate', (event, url) => {
    if (!url.startsWith('file://')) {
      event.preventDefault();
      if (/^https?:/i.test(url)) shell.openExternal(url);
    }
  });
}

ipcMain.on('matlex-window-control', (event, action) => {
  const win = BrowserWindow.fromWebContents(event.sender);
  if (!win) return;
  if (action === 'minimize') win.minimize();
  if (action === 'maximize') win.isMaximized() ? win.unmaximize() : win.maximize();
  if (action === 'close') win.close();
});

app.whenReady().then(() => {
  app.setAppUserModelId('com.materialex.desktop');
  ensureDesktopShortcut();
  createWindow();
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
