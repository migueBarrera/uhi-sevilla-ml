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
    if (mapRef.current) {
      mapRef.current.setView([37.3886, -5.9823], 13);
    } else {
      setZoomTarget({ center: [37.3886, -5.9823], zoom: 13 });
    }
  }

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
      <SidePanel barrioName={selectedBarrio} data={getSelectedBarrioData()} onClose={handleVolver} datasetStats={datasetStats} />
      <Legend items={colorLegend} />
      <ErrorBanner error={error} />
      <BackButton visible={!!selectedBarrio} onClick={handleVolver} />

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

        <PointsLayer points={points} getColor={getColor} />
      </MapContainer>
    </div>
  );
}
