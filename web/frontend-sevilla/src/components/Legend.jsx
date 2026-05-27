import React from 'react';

export default function Legend({ items }) {
  return (
    <div style={{
      position: 'absolute',
      bottom: 30,
      left: 30,
      zIndex: 1002,
      background: 'rgba(255,255,255,0.95)',
      border: '1px solid #bbb',
      borderRadius: 8,
      padding: '12px 18px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
      minWidth: 120
    }}>
      <b style={{ fontSize: 15 }}>Temperatura (°C)</b>
      <div style={{ marginTop: 8 }}>
        {items.map((item, idx) => (
          <div key={idx} style={{ display: 'flex', alignItems: 'center', marginBottom: 4 }}>
            <span style={{
              display: 'inline-block',
              width: 22,
              height: 16,
              background: item.color,
              border: '1px solid #888',
              marginRight: 8,
              borderRadius: 3
            }} />
            <span style={{ fontSize: 13 }}>{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
