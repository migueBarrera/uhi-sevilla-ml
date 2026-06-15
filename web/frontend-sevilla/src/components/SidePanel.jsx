import React, { useState, useEffect } from 'react';
import { predictTemperature } from '../services/predictService';
import SidePanelSimpleSection from './SidePanelSimpleSection';
import SidePanelDetailedSection from './SidePanelDetailedSection';

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
  const [viewMode, setViewMode] = useState('detailed');
  const [scenarioControls, setScenarioControls] = useState({
    reforestation: 0,
    densification: 0,
    coolRoofs: 0,
  });

  function clamp(value, min, max) {
    return Math.min(max, Math.max(min, value));
  }

  function computeScenarioValues(baseValues, controls) {
    const reforestation = Number(controls.reforestation) || 0;
    const densification = Number(controls.densification) || 0;
    const coolRoofs = Number(controls.coolRoofs) || 0;

    const baseNDVI = Number(baseValues.NDVI) || 0;
    const baseNDBI = Number(baseValues.NDBI) || 0;
    const baseTree = Number(baseValues.Tree_Density_50m) || 0;
    const baseBuildingDensity = Number(baseValues.Building_Density_100m) || 0;
    const baseBuildingHeight = Number(baseValues.Avg_Building_Height_100m) || 0;
    const baseAlbedo = Number(baseValues.Albedo) || 0;

    const ndviDeltaRef = (reforestation / 100) * 0.40;
    const ndviDeltaDense = densification > 0 ? (densification / 100) * 0.12 : 0;
    const nextNDVI = clamp(baseNDVI + ndviDeltaRef - ndviDeltaDense, 0.02, 0.65);

    const nextTree = clamp(baseTree + Math.round((reforestation / 100) * 10), 0, 12);

    const ndbiDeltaRef = (reforestation / 100) * 0.25;
    const ndbiDeltaDense = (densification / 100) * 0.30;
    const nextNDBI = clamp(baseNDBI - ndbiDeltaRef + ndbiDeltaDense, -0.15, 0.95);

    const albedoDeltaRef = (reforestation / 100) * 0.03;
    const albedoDeltaCool = (coolRoofs / 100) * 0.24;
    const nextAlbedo = clamp(baseAlbedo - albedoDeltaRef + albedoDeltaCool, 0, 0.40);

    const densityFactor = densification >= 0 ? 40 : 20;
    const nextBuildingDensity = clamp(baseBuildingDensity + (densification / 100) * densityFactor, 0, 85);

    const heightFactor = densification >= 0 ? 15.0 : 6.0;
    const nextBuildingHeight = clamp(baseBuildingHeight + (densification / 100) * heightFactor, 0, 30.0);

    return {
      ...baseValues,
      NDVI: nextNDVI,
      NDBI: nextNDBI,
      Albedo: nextAlbedo,
      Tree_Density_50m: nextTree,
      Building_Density_100m: nextBuildingDensity,
      Avg_Building_Height_100m: nextBuildingHeight,
    };
  }

  function getPercentChange(key) {
    const original = Number(defaultValues[key]);
    const current = Number(modifiedValues[key]);
    if (Number.isNaN(original) || Number.isNaN(current)) return null;
    if (original === 0) return current === 0 ? 0 : null;
    return ((current - original) / Math.abs(original)) * 100;
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
    setScenarioControls({ reforestation: 0, densification: 0, coolRoofs: 0 });
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
    setScenarioControls({ reforestation: 0, densification: 0, coolRoofs: 0 });
    setModifiedValues({ ...defaultValues });
    setPredictedTemp(null);
    onPredictedPointsChange([]);
  }

  function handleScenarioControlChange(key, raw) {
    const value = Number(raw);
    setScenarioControls(prev => {
      const next = { ...prev, [key]: value };
      setModifiedValues(computeScenarioValues(defaultValues, next));
      return next;
    });
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

      const deltaByField = {};
      predictorFields.forEach(field => {
        const original = Number(defaultValues[field]);
        const modified = Number(modifiedValues[field]);
        if (Number.isNaN(original) || Number.isNaN(modified)) {
          deltaByField[field] = 0;
          return;
        }
        deltaByField[field] = modified - original;
      });

      const rows = Array.isArray(points) ? points : [];
      const predictionRows = rows.map(row => {
        const transformed = { ...row };
        predictorFields.forEach(field => {
          const baseValue = Number(row[field] ?? data[field] ?? 0);
          const delta = Number(deltaByField[field]) || 0;
          const candidate = baseValue + delta;

          if (datasetStats && datasetStats[field] && typeof datasetStats[field].min === 'number' && typeof datasetStats[field].max === 'number') {
            transformed[field] = clamp(candidate, datasetStats[field].min, datasetStats[field].max);
          } else {
            transformed[field] = candidate;
          }

          if (Number.isNaN(transformed[field])) {
            transformed[field] = Number.isNaN(baseValue) ? 0 : baseValue;
          }
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
      <h2 style={{marginTop:0, marginBottom: 10, fontSize: 26, color: '#a50f15'}}>{barrioName}</h2>
      <div style={{ marginBottom: 16 }}>
        <div
          style={{
            display: 'inline-flex',
            gap: 6,
            padding: 4,
            borderRadius: 10,
            background: '#f5f7fb',
            border: '1px solid #e5e9f2'
          }}
        >
          <button
            onClick={() => setViewMode('simple')}
            style={{
              border: 'none',
              borderRadius: 8,
              padding: '6px 10px',
              fontSize: 13,
              fontWeight: 700,
              cursor: 'pointer',
              background: viewMode === 'simple' ? '#2b6cb0' : 'transparent',
              color: viewMode === 'simple' ? '#fff' : '#4a5568'
            }}
          >
            Simple
          </button>
          <button
            onClick={() => setViewMode('detailed')}
            style={{
              border: 'none',
              borderRadius: 8,
              padding: '6px 10px',
              fontSize: 13,
              fontWeight: 700,
              cursor: 'pointer',
              background: viewMode === 'detailed' ? '#2b6cb0' : 'transparent',
              color: viewMode === 'detailed' ? '#fff' : '#4a5568'
            }}
          >
            Detallado
          </button>
        </div>
      </div>

      {viewMode === 'simple' && (
        <SidePanelSimpleSection
          scenarioControls={scenarioControls}
          onScenarioControlChange={handleScenarioControlChange}
          onReset={handleReset}
        />
      )}

      {viewMode === 'detailed' && (
        <SidePanelDetailedSection
          mainVars={mainVars}
          defaultValues={defaultValues}
          modifiedValues={modifiedValues}
          friendlyNames={friendlyNames}
          formatValue={formatValue}
          getRangeForKey={getRangeForKey}
          getPercentChange={getPercentChange}
          handleSliderChange={handleSliderChange}
          onReset={handleReset}
        />
      )}

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
