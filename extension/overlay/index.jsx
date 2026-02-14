import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './styles.css';

const containerId = 'yta-react-root';
let container = document.getElementById(containerId);
if (!container) {
    container = document.createElement('div');
    container.id = containerId;
    container.style.position = 'absolute';
    container.style.top = '80px';
    container.style.right = '20px';
    container.style.zIndex = '999999';
    document.body.appendChild(container);
}

const root = createRoot(container);
root.render(<App videoUrl={window.location.href} />);
