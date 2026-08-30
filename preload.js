const { contextBridge } = require('electron');
contextBridge.exposeInMainWorld('MatLexDesktop', Object.freeze({
  platform: process.platform,
  desktop: true,
  version: '11.3.1'
}));
