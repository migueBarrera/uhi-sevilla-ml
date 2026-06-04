import React, { useLayoutEffect, useRef, useState } from 'react';

export default function InfoHoverIcon({ text }) {
  const [isOpen, setIsOpen] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState({ left: 0, top: 0, ready: false });
  const triggerRef = useRef(null);
  const tooltipRef = useRef(null);

  function showTooltip() {
    setIsOpen(true);
  }

  function hideTooltip() {
    setIsOpen(false);
  }

  function renderTooltipContent(content) {
    if (!content) return null;

    if (typeof content === 'string') {
      return <div style={{ whiteSpace: 'pre-line' }}>{content}</div>;
    }

    const { title, subtitle, summary, points = [] } = content;

    return (
      <div>
        {title ? (
          <div style={{ fontWeight: 800, fontSize: 13, marginBottom: 4, color: '#111827' }}>
            {title}
          </div>
        ) : null}

        {subtitle ? (
          <div style={{ fontStyle: 'italic', fontWeight: 600, marginBottom: 6, color: '#1f2937' }}>
            {subtitle}
          </div>
        ) : null}

        {summary ? (
          <div style={{ marginBottom: points.length ? 8 : 0, color: '#111827' }}>{summary}</div>
        ) : null}

        {points.length > 0 ? (
          <ul style={{ margin: 0, paddingLeft: 16, color: '#111827' }}>
            {points.map((item, idx) => {
              if (!item) return null;
              const pointText = typeof item === 'string' ? item : item.text;
              const label = typeof item === 'object' ? item.label : null;
              return (
                <li key={idx} style={{ marginBottom: idx === points.length - 1 ? 0 : 6 }}>
                  {label ? <strong>{label}: </strong> : null}
                  <span>{pointText}</span>
                </li>
              );
            })}
          </ul>
        ) : null}
      </div>
    );
  }

  useLayoutEffect(() => {
    if (!isOpen) return;

    function updatePosition() {
      if (!triggerRef.current || !tooltipRef.current) return;

      const triggerRect = triggerRef.current.getBoundingClientRect();
      const tooltipRect = tooltipRef.current.getBoundingClientRect();
      const gap = 8;
      const margin = 8;

      let left = triggerRect.right + gap;
      let top = triggerRect.top + triggerRect.height / 2 - tooltipRect.height / 2;

      // If there is no room on the right, place tooltip on the left.
      if (left + tooltipRect.width + margin > window.innerWidth) {
        left = triggerRect.left - tooltipRect.width - gap;
      }

      // Clamp to viewport horizontally and vertically.
      if (left < margin) left = margin;
      if (top < margin) top = margin;
      if (top + tooltipRect.height + margin > window.innerHeight) {
        top = window.innerHeight - tooltipRect.height - margin;
      }

      setTooltipPosition({ left, top, ready: true });
    }

    updatePosition();
    window.addEventListener('resize', updatePosition);
    window.addEventListener('scroll', updatePosition, true);

    return () => {
      window.removeEventListener('resize', updatePosition);
      window.removeEventListener('scroll', updatePosition, true);
      setTooltipPosition(prev => ({ ...prev, ready: false }));
    };
  }, [isOpen]);

  return (
    <span
      ref={triggerRef}
      onMouseEnter={showTooltip}
      onMouseLeave={hideTooltip}
      style={{
        marginLeft: 6,
        position: 'relative',
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}
    >
      <span
        onFocus={showTooltip}
        onBlur={hideTooltip}
        tabIndex={0}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: 20,
          height: 20,
          borderRadius: '50%',
          background: '#f3f6ff',
          color: '#2b6cb0',
          fontSize: 12,
          cursor: 'help',
          boxShadow: '0 1px 2px rgba(0,0,0,0.06)',
          outline: 'none'
        }}
        aria-label="Mas informacion"
      >
        i
      </span>

      {isOpen && text && (
        <div
          ref={tooltipRef}
          style={{
            position: 'fixed',
            left: tooltipPosition.left,
            top: tooltipPosition.top,
            width: 320,
            maxWidth: 'min(320px, 70vw)',
            padding: '10px 12px',
            borderRadius: 10,
            background: '#ffffff',
            border: '1px solid #e5e7eb',
            boxShadow: '0 10px 25px rgba(0, 0, 0, 0.18)',
            color: '#111111',
            fontSize: 13,
            lineHeight: 1.4,
            zIndex: 4000,
            visibility: tooltipPosition.ready ? 'visible' : 'hidden'
          }}
          role="tooltip"
        >
          {renderTooltipContent(text)}
        </div>
      )}
    </span>
  );
}
