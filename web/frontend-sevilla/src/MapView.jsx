import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

import SetMapRef from './components/SetMapRef';
import Legend from './components/Legend';
import ErrorBanner from './components/ErrorBanner';
import BackButton from './components/BackButton';
import SidePanel from './components/SidePanel';
import BarrioLayers from './components/BarrioLayers';
import PointsLayer from './components/PointsLayer';
import { colorLegend, getColor, barrioStyle, parseCSV } from './utils/mapUtils';

export default function MapView() {
  const [error, setError] = useState(null);
  const [geojson, setGeojson] = useState(null);
  const [points, setPoints] = useState([]);
  const [predictedPoints, setPredictedPoints] = useState([]);
  const [pointsMode, setPointsMode] = useState('original');
  const [markerOpacity, setMarkerOpacity] = useState(0.85);
  const [zoomTarget, setZoomTarget] = useState(null);
  const [selectedBarrio, setSelectedBarrio] = useState(null);
  const mapRef = useRef();

  function getSelectedBarrioData() {
    if (!geojson || !selectedBarrio) return null;
    return geojson.features.find(f => f.properties.name === selectedBarrio)?.properties || null;
  }

  useEffect(() => {
    try {
      fetch('/assets/mapa_barrios_temperatura.geojson')
        .then(res => res.json())
        .then(setGeojson);
    } catch (e) {
      setError('Error cargando el GeoJSON de barrios');
      console.error('GeoJSON error:', e);
    }
  }, []);

  useEffect(() => {
    if (zoomTarget && mapRef.current) {
      const map = mapRef.current;
      if (zoomTarget.bounds) {
        map.fitBounds(zoomTarget.bounds, { maxZoom: 16 });
      } else if (zoomTarget.center) {
        map.setView(zoomTarget.center, 16);
      }
    }
  }, [zoomTarget]);

  function handleBarrioClick(feature, layer) {
    try {
      setSelectedBarrio(feature.properties.name);
      const coords = feature.geometry.coordinates[0].map(([lon, lat]) => [lat, lon]);
      setZoomTarget({ bounds: coords });
      const barrio = feature.properties.name.replace(/ /g, '_').toLowerCase();
      const csvPath = `/assets/barrios/detail_${barrio}.csv`;
      fetch(csvPath)
        .then(res => res.ok ? res.text() : null)
        .then(text => {
          if (text) setPoints(parseCSV(text));
          else setPoints([]);
          setPredictedPoints([]);
          setPointsMode('original');
        })
        .catch(e => {
          setError('Error cargando el CSV de puntos para el barrio');
          console.error('CSV error:', e);
        });
    } catch (e) {
      setError('Error procesando el click en el barrio');
      console.error('Click error:', e);
    }
  }

  function handleVolver() {
    setSelectedBarrio(null);
    setPoints([]);
    setPredictedPoints([]);
    setPointsMode('original');
    if (mapRef.current) {
      mapRef.current.setView([37.3886, -5.9823], 13);
    } else {
      setZoomTarget({ center: [37.3886, -5.9823], zoom: 13 });
    }
  }

  function handlePredictedPointsChange(newPredictedPoints) {
    const nextPredictedPoints = Array.isArray(newPredictedPoints) ? newPredictedPoints : [];
    setPredictedPoints(nextPredictedPoints);
    setPointsMode(nextPredictedPoints.length > 0 ? 'predicted' : 'original');
  }

  const visiblePoints = pointsMode === 'predicted' && predictedPoints.length > 0 ? predictedPoints : points;

  // Dataset stats (from provided summary) to set sensible slider ranges
  const datasetStats = {
    NDVI: { min: -1.0, max: 0.927826 },
    NDBI: { min: -0.6302, max: 1.0 },
    Albedo: { min: 0.002293, max: 0.808436 },
    D2W_meters: { min: 0.0, max: 1368.831619 },
    D2R_meters: { min: 0.023918, max: 2743.999249 },
    Tree_Density_50m: { min: 0.0, max: 7.0 },
  };

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <SidePanel barrioName={selectedBarrio} data={getSelectedBarrioData()} points={points} onClose={handleVolver} datasetStats={datasetStats} markerOpacity={markerOpacity} onMarkerOpacityChange={setMarkerOpacity} onPredictedPointsChange={handlePredictedPointsChange} />
      <Legend items={colorLegend} />
      <ErrorBanner error={error} />
      <BackButton visible={!!selectedBarrio} onClick={handleVolver} />

      {!!selectedBarrio && (
        <div style={{
          position: 'absolute',
          top: 12,
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 2100,
          display: 'flex',
          borderRadius: 999,
          overflow: 'hidden',
          border: '1px solid #d7dfef',
          background: '#fff',
          boxShadow: '0 4px 12px rgba(0,0,0,0.10)'
        }}>
          <button
            onClick={() => setPointsMode('original')}
            style={{
              border: 'none',
              padding: '8px 14px',
              cursor: 'pointer',
              fontWeight: 700,
              background: pointsMode === 'original' ? '#2b6cb0' : 'transparent',
              color: pointsMode === 'original' ? '#fff' : '#2b6cb0'
            }}
          >
            Original
          </button>
          <button
            onClick={() => setPointsMode('predicted')}
            disabled={predictedPoints.length === 0}
            style={{
              border: 'none',
              padding: '8px 14px',
              cursor: predictedPoints.length > 0 ? 'pointer' : 'not-allowed',
              fontWeight: 700,
              background: pointsMode === 'predicted' ? '#2b6cb0' : 'transparent',
              color: pointsMode === 'predicted' ? '#fff' : (predictedPoints.length > 0 ? '#2b6cb0' : '#97a9c8')
            }}
          >
            Predicho
          </button>
        </div>
      )}

      <MapContainer center={[37.3886, -5.9823]} zoom={12} style={{ width: '100%', height: '100%' }} whenCreated={map => (mapRef.current = map)}>
        <SetMapRef mapRef={mapRef} />
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
        />

        <BarrioLayers
          geojson={geojson}
          selectedBarrio={selectedBarrio}
          style={barrioStyle}
          onBarrioClick={handleBarrioClick}
          setError={setError}
        />

        <PointsLayer points={visiblePoints} getColor={getColor} markerOpacity={markerOpacity} />
      </MapContainer>
    </div>
  );
}
