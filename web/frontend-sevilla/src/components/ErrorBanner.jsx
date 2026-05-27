import React from 'react';

export default function ErrorBanner({ error }) {
  if (!error) return null;
  return (
    <div style={{ position: 'absolute', zIndex: 1000, background: '#fff0f0', color: '#b00', padding: 16, border: '1px solid #b00', top: 20, left: '50%', transform: 'translateX(-50%)', maxWidth: 400 }}>
      <b>Ocurrió un error:</b><br />
      {error}
    </div>
  );
}
