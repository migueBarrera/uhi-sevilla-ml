import React, { useState, useEffect } from 'react';
import { predictTemperature } from '../services/predictService';

function formatValue(v) {
  const num = Number(v);
  return !isNaN(num) && v !== '' && v !== null ? num.toFixed(2) : v;
}

const friendlyNames = {
  'NDVI': 'Índice de Vegetación (NDVI)',
  'NDBI': 'Índice de Construcción (NDBI)',
  'Albedo': 'Albedo',
  'D2W_meters': 'Distancia a Agua (m)',
  'LST_Target': 'Temperatura Superficie (°C)',
  'Tree_Density_50m': 'Densidad de Árboles (50m)',
  'Building_Density_100m': 'Densidad de Edificios (100m)',
  'Avg_Building_Height_100m': 'Altura Media Edificios (100m)',
};

const explanations = {
  'NDVI': 'Índice de vegetación: valores altos indican más vegetación, lo que suele reducir la temperatura superficial.',
  'NDBI': 'Índice de construcción: valores altos indican mayor presencia de edificios y superficies selladas, lo que suele aumentar la temperatura.',
  'Albedo': 'Porcentaje de radiación reflejada: valores altos reflejan más luz y pueden reducir la temperatura.',
  'D2W_meters': 'Distancia al agua: cuanto más cerca del agua, mayor efecto refrescante.',
  'LST_Target': 'Temperatura superficial media estimada para el barrio.',
  'Tree_Density_50m': 'Cantidad de árboles en un radio de 50 metros: más árboles suelen reducir la temperatura.',
  'Building_Density_100m': 'Cantidad de edificios en un radio de 100 metros: más edificios suelen aumentar la temperatura.',
  'Avg_Building_Height_100m': 'Altura media de los edificios en 100 metros: puede influir en la sombra y la ventilación.',
};

export default function SidePanel({ barrioName, data, points = [], onClose, datasetStats, markerOpacity = 0.85, onMarkerOpacityChange = () => {}, onPredictedPointsChange = () => {} }) {
  if (!barrioName) return null;
  if (!data) return (
    <div style={{
      position: 'absolute',
      top: 0,
      right: 0,
      height: '100%',
      width: 420,
      maxHeight: '100vh',
      boxSizing: 'border-box',
      background: '#fff',
      boxShadow: '-2px 0 12px rgba(0,0,0,0.10)',
      zIndex: 2000,
      padding: '36px 32px 28px 32px',
      overflowY: 'auto',
      transition: 'transform 0.3s',
      borderLeft: '1px solid #eee',
      display: 'flex',
      flexDirection: 'column',
    }}>
      <button
        onClick={onClose}
        aria-label="Cerrar"
        style={{
          position: 'absolute',
          top: 12,
          left: 12,
          border: 'none',
          background: 'transparent',
          fontSize: 20,
          cursor: 'pointer',
          color: '#666'
        }}
      >
        ✕
      </button>
      <h2 style={{marginTop:0, marginBottom: 18, fontSize: 26, color: '#a50f15'}}>{barrioName}</h2>
      <div>No hay datos del barrio.</div>
    </div>
  );

  const excludeVars = ['name', 'D2R_HighCapacity_m', 'D2R_Urban_m', 'LST_Target'];
  const mainVars = Object.keys(data).filter(key => !excludeVars.includes(key));
  const tempValue = data && data.LST_Target !== undefined ? formatValue(data.LST_Target) : '—';
  const tempDisplay = tempValue === '—' ? '—' : `${tempValue} °C`;

  const [defaultValues, setDefaultValues] = useState({});
  const [modifiedValues, setModifiedValues] = useState({});
  const [predictLoading, setPredictLoading] = useState(false);
  const [predictedTemp, setPredictedTemp] = useState(null);

  function getPercentChange(key) {
    const original = Number(defaultValues[key]);
    const current = Number(modifiedValues[key]);
    if (Number.isNaN(original) || Number.isNaN(current)) return null;
    if (original === 0) return current === 0 ? 0 : null;
    return ((current - original) / Math.abs(original)) * 100;
  }

  function applyPercentChange(value, percent) {
    const num = Number(value);
    if (Number.isNaN(num) || percent === null || percent === undefined) return num;
    return num * (1 + percent / 100);
  }

  useEffect(() => {
    if (!data) return;
    const defs = {};
    mainVars.forEach(k => {
      const v = data[k];
      const num = Number(v);
      defs[k] = !isNaN(num) ? num : v;
    });
    setDefaultValues(defs);
    setModifiedValues({ ...defs });
    setPredictedTemp(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data]);

  function getRangeForKey(key, val) {
    // Prefer datasetStats if provided
    if (datasetStats && datasetStats[key] && typeof datasetStats[key].min === 'number' && typeof datasetStats[key].max === 'number') {
      let min = datasetStats[key].min;
      let max = datasetStats[key].max;
      // Round near-zero mins to 0
      if (Math.abs(min) < 0.01) min = 0;
      // Round near-one maxes to 1
      if (Math.abs(1 - max) < 0.01) max = 1;
      const range = Math.abs(max - min);
      let step = +(range / 100).toFixed(2);
      if (step < 0.01) step = 0.01;
      return { min, max, step };
    }

    const num = Number(val);
    if (isNaN(num)) return null;
    switch (key) {
      case 'NDVI': return { min: -1, max: 1, step: 0.01 };
      case 'NDBI': return { min: -1, max: 1, step: 0.01 };
      case 'Albedo': return { min: 0, max: 1, step: 0.01 };
      case 'D2W_meters': return { min: 0, max: Math.max(500, Math.ceil(num * 2)), step: 1 };
      case 'Tree_Density_50m': return { min: 0, max: Math.max(1, Math.ceil(num * 2)), step: 0.01 };
      case 'Building_Density_100m': return { min: 0, max: Math.max(1, Math.ceil(num * 2)), step: 0.01 };
      case 'Avg_Building_Height_100m': return { min: 0, max: Math.max(50, Math.ceil(num * 2)), step: 0.1 };
      default:
        if (num === 0) return { min: 0, max: 100, step: 1 };
        const abs = Math.abs(num);
        return { min: Math.floor(num - abs * 0.5), max: Math.ceil(num + abs * 0.5), step: abs < 1 ? 0.01 : 1 };
    }
  }

  function handleSliderChange(key, raw) {
    const v = raw === '' ? '' : Number(raw);
    setModifiedValues(prev => ({ ...prev, [key]: v }));
  }

  function handleReset() {
    setModifiedValues({ ...defaultValues });
  }

  const isModified = Object.keys(defaultValues).length > 0 && Object.keys(defaultValues).some(k => defaultValues[k] !== modifiedValues[k]);

  async function handlePredict() {
    if (!isModified) return;
    setPredictLoading(true);
    setPredictedTemp(null);
    try {
      const predictorFields = [
        'NDVI',
        'NDBI',
        'Albedo',
        'D2W_meters',
        'Tree_Density_50m',
        'Building_Density_100m',
        'Avg_Building_Height_100m',
      ];

      const percentByField = {};
      predictorFields.forEach(field => {
        percentByField[field] = getPercentChange(field);
      });

      const rows = Array.isArray(points) ? points : [];
      const predictionRows = rows.map(row => {
        const transformed = { ...row };
        predictorFields.forEach(field => {
          const pct = percentByField[field];
          const baseValue = row[field] ?? data[field] ?? 0;
          const updated = applyPercentChange(baseValue, pct);
          transformed[field] = Number.isNaN(updated) ? Number(baseValue) || 0 : updated;
        });

        return {
          NDVI: Number(transformed.NDVI) || 0,
          NDBI: Number(transformed.NDBI) || 0,
          Albedo: Number(transformed.Albedo) || 0,
          D2W_meters: Number(transformed.D2W_meters) || 0,
          D2R_HighCapacity_m: Number(row.D2R_HighCapacity_m ?? data.D2R_HighCapacity_m) || 0,
          D2R_Urban_m: Number(row.D2R_Urban_m ?? data.D2R_Urban_m) || 0,
          Tree_Density_50m: Number(transformed.Tree_Density_50m) || 0,
          Building_Density_100m: Number(transformed.Building_Density_100m) || 0,
          Avg_Building_Height_100m: Number(transformed.Avg_Building_Height_100m) || 0,
        };
      });

      if (predictionRows.length === 0) {
        console.warn('[Predict] No points available for prediction');
        return;
      }

      // Delegate network call to predict service
      const result = await predictTemperature(predictionRows);
      if (result && result.success && Array.isArray(result.predicted_array) && result.predicted_array.length > 0) {
        const predictedArray = result.predicted_array.map(v => Number(v)).filter(v => !Number.isNaN(v));
        const avg = predictedArray.reduce((acc, v) => acc + v, 0) / predictedArray.length;
        const p = avg.toFixed(2);
        console.log('[Predict]', new Date().toISOString(), '-> predicted (service) - avg:', p, 'count:', predictedArray.length);
        setPredictedTemp(`${p} °C`);

        const predictedPointsWithTemp = rows.map((row, idx) => ({
          ...row,
          LST_Target: predictedArray[idx] ?? row.LST_Target,
        }));
        onPredictedPointsChange(predictedPointsWithTemp);
      } else {
        console.error('[Predict] Service returned unexpected result', result);
      }
    } catch (e) {
      console.error('[Predict] Error', new Date().toISOString(), e);
    } finally {
      setPredictLoading(false);
    }
  }

  return (
    <div style={{
      position: 'absolute',
      top: 0,
      right: 0,
      height: '100%',
      width: 520,
      maxHeight: '100vh',
      boxSizing: 'border-box',
      background: '#fff',
      boxShadow: '-2px 0 12px rgba(0,0,0,0.10)',
      zIndex: 2000,
      padding: '36px 32px 28px 32px',
      overflowY: 'auto',
      transition: 'transform 0.3s',
      borderLeft: '1px solid #eee',
      display: 'flex',
      flexDirection: 'column',
    }}>
      <button
        onClick={onClose}
        aria-label="Cerrar"
        style={{
          position: 'absolute',
          top: 12,
          left: 12,
          border: 'none',
          background: 'transparent',
          fontSize: 20,
          cursor: 'pointer',
          color: '#666'
        }}
      >
        ✕
      </button>
      <h2 style={{marginTop:0, marginBottom: 18, fontSize: 26, color: '#a50f15'}}>{barrioName}</h2>
      <div style={{marginBottom: 18}}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <b style={{fontSize:18, color:'#234567'}}>Indicadores principales</b>
          <button onClick={handleReset} style={{ background: 'transparent', border: 'none', color: '#2b6cb0', cursor: 'pointer', fontSize: 13 }}>restablecer</button>
        </div>
        <table style={{width:'100%', fontSize:16, borderCollapse:'collapse', marginTop:8, marginBottom:8}}>
          <tbody>
            {mainVars.map(key => {
              const def = defaultValues[key];
              const mod = modifiedValues[key];
              const current = mod !== undefined ? mod : def;
              const range = getRangeForKey(key, def);
              const isNumeric = range !== null;
              return (
                <tr key={key} style={{ verticalAlign: 'middle' }}>
                  <td style={{fontWeight:600, padding:'6px 10px 6px 0', color:'#555', width: '40%'}}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <span style={{ textAlign: 'left' }}>{friendlyNames[key] || key.replace(/_/g,' ')}</span>
                      <span
                        title={explanations[key] || ''}
                        style={{
                          marginLeft: 6,
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
                          boxShadow: '0 1px 2px rgba(0,0,0,0.06)'
                        }}
                        aria-hidden
                      >
                        i
                      </span>
                    </div>
                  </td>
                  <td style={{padding:'4px 0', width: '60%'}}>
                    {isNumeric ? (
                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                          <div style={{ fontSize: 15 }}>{formatValue(current)}</div>
                          <div style={{ fontSize: 12, color: '#2b6cb0', fontWeight: 600 }}>
                            {(() => {
                              const pct = getPercentChange(key);
                              if (pct === null) return '—';
                              const sign = pct > 0 ? '+' : '';
                              return `${sign}${pct.toFixed(1)}%`;
                            })()}
                          </div>
                        </div>
                        <input
                          type="range"
                          min={range.min}
                          max={range.max}
                          step={range.step}
                          value={current}
                          onChange={e => handleSliderChange(key, e.target.value)}
                          style={{ width: '100%' }}
                        />
                      </div>
                    ) : (
                      <div style={{ textAlign: 'right' }}>{String(current)}</div>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Temperaturas: Real (izquierda) y Predicha (derecha) */}
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, marginTop: 8 }}>
        <div style={{ flex: 1, textAlign: 'center', padding: 12, background: '#fafafa', borderRadius: 8 }}>
          <div style={{ fontSize: 13, color: '#555', marginBottom: 6 }}>Temperatura Real</div>
          <div style={{ fontSize: 34, fontWeight: 800, color: '#a50f15' }}>{tempDisplay}</div>
        </div>
        <div style={{ flex: 1, textAlign: 'center', padding: 12, background: '#fafafa', borderRadius: 8 }}>
          <div style={{ fontSize: 13, color: '#555', marginBottom: 6 }}>Temperatura Predicha</div>
          <div style={{ fontSize: 34, fontWeight: 800, color: '#a50f15' }}>{predictedTemp || tempDisplay}</div>
        </div>
      </div>
      <div style={{ marginTop: 16, display: 'flex', justifyContent: 'center' }}>
        <button
          onClick={handlePredict}
          disabled={!isModified || predictLoading || !Array.isArray(points) || points.length === 0}
          style={{
            padding: '10px 18px',
            borderRadius: 8,
            border: 'none',
            cursor: (isModified && !predictLoading && Array.isArray(points) && points.length > 0) ? 'pointer' : 'not-allowed',
            background: (isModified && !predictLoading && Array.isArray(points) && points.length > 0) ? '#2b6cb0' : '#e6eefc',
            color: (isModified && !predictLoading && Array.isArray(points) && points.length > 0) ? '#fff' : '#8aa6d8',
            fontWeight: 700,
            fontSize: 15
          }}
        >
          {predictLoading ? 'Prediciendo...' : 'Predecir temperatura'}
        </button>
      </div>

      {/* Opacidad de marcadores (debajo del botón de predicción) */}
      <div style={{ marginTop: 12, marginBottom: 8 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
          <div style={{ fontSize: 14, color: '#555' }}>Opacidad marcadores</div>
          <div style={{ fontWeight: 700 }}>{Math.round((markerOpacity || 0) * 100)}%</div>
        </div>
        <input
          type="range"
          min={0}
          max={1}
          step={0.01}
          value={markerOpacity}
          onChange={e => onMarkerOpacityChange(Number(e.target.value))}
          style={{ width: '100%' }}
        />
      </div>
    </div>
  );
}
