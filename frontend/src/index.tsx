import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import SpreadsheetApp from './SpreadsheetApp';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <SpreadsheetApp />
  </React.StrictMode>
);