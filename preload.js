const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('MatLexDesktop', Object.freeze({
  platform: process.platform,
  desktop: true,
  version: '11.4.1',
  window: Object.freeze({
    minimize: () => ipcRenderer.send('matlex-window-control', 'minimize'),
    toggleMaximize: () => ipcRenderer.send('matlex-window-control', 'maximize'),
    close: () => ipcRenderer.send('matlex-window-control', 'close'),
    onState: (callback) => {
      const handler = (_event, state) => callback?.(state);
      ipcRenderer.on('matlex-window-state', handler);
      return () => ipcRenderer.removeListener('matlex-window-state', handler);
    }
  })
}));
