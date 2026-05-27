import React from 'react';

export default function BackButton({ visible, onClick }) {
  if (!visible) return null;
  return (
    <button
      onClick={onClick}
      style={{
        position: 'absolute',
        zIndex: 1001,
        top: 30,
        left: 30,
        padding: '10px 20px',
        background: '#fff',
        border: '2px solid #222',
        borderRadius: 8,
        cursor: 'pointer',
        fontWeight: 700,
        fontSize: 17,
        color: '#111',
        boxShadow: '0 2px 8px rgba(0,0,0,0.10)',
        letterSpacing: 0.5,
        textShadow: 'none'
      }}
    >
      ← Volver
    </button>
  );
}
