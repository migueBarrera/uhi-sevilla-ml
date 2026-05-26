import React, { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON, Marker, Tooltip, useMap, CircleMarker } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

export default function MapView() {
        // Devuelve el objeto del barrio seleccionado
        function getSelectedBarrioData() {
          if (!geojson || !selectedBarrio) return null;
          return geojson.features.find(f => f.properties.name === selectedBarrio)?.properties || null;
        }
      // Leyenda de colores para la temperatura
      const colorLegend = [
        { label: '≥ 50°C', color: '#67000d' },
        { label: '47–49.9°C', color: '#a50f15' },
        { label: '44–46.9°C', color: '#de2d26' },
        { label: '41–43.9°C', color: '#fb6a4a' },
        { label: '38–40.9°C', color: '#fc9272' },
        { label: '35–37.9°C', color: '#fcbba1' },
        { label: '< 35°C', color: '#fee5d9' },
      ];
    const [error, setError] = useState(null);
  // Utilidad para colorear barrios según temperatura
  function getColor(temp) {
    // Ajustado para el rango real de Sevilla (40-50°C) con margen +/- 5°C
    return temp >= 50 ? '#67000d' // Extremo (oscuro/sangre)
      : temp >= 47 ? '#a50f15'    // Muy alto
      : temp >= 44 ? '#de2d26'    // Alto
      : temp >= 41 ? '#fb6a4a'    // Medio-Alto
      : temp >= 38 ? '#fc9272'    // Medio
      : temp >= 35 ? '#fcbba1'    // Moderado
      : '#fee5d9';                // Suave (fuera del rango crítico)
  }

  const style = feature => ({
    fillColor: getColor(feature.properties.LST_Target),
    weight: 1,
    opacity: 1,
    color: '#234567',
    fillOpacity: 0.7,
    cursor: 'pointer',
  });

  const [geojson, setGeojson] = useState(null);
  const [points, setPoints] = useState([]);
  const [zoomTarget, setZoomTarget] = useState(null); // {center: [lat, lon], bounds: [[lat, lon], ...]}
  const [selectedBarrio, setSelectedBarrio] = useState(null);
  const mapRef = useRef();

  useEffect(() => {
    try {
      fetch('/assets/mapa_barrios_temperatura.geojson')
        .then(res => res.json())
        .then(setGeojson);
    } catch (e) {
      setError('Error cargando el GeoJSON de barrios');
      console.error('GeoJSON error:', e);
    }
  }, [])
    
  // Efecto para hacer zoom cuando cambia zoomTarget
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

  // Parsear CSV simple (asume cabecera y separador coma)
  function parseCSV(text) {
    const lines = text.trim().split('\n');
    const headers = lines[0].split(',');
    return lines.slice(1).map(line => {
      const values = line.split(',');
      const obj = {};
      headers.forEach((h, i) => obj[h] = values[i]);
      return obj;
    });
  }

  // Handler click barrio
  function handleBarrioClick(feature, layer) {
    try {
      setSelectedBarrio(feature.properties.name);
      // Zoom a los bounds del barrio
      const coords = feature.geometry.coordinates[0].map(([lon, lat]) => [lat, lon]);
      setZoomTarget({ bounds: coords });
      // Cargar puntos CSV
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

  // Volver a la vista general
  function handleVolver() {
    setSelectedBarrio(null);
    setPoints([]);
    // Zoom más cercano al volver a la vista general
    if (mapRef.current) {
      mapRef.current.setView([37.3886, -5.9823], 13); // zoom 13 en vez de 12
    } else {
      setZoomTarget({ center: [37.3886, -5.9823], zoom: 13 });
    }
  }

  // Componente para obtener instancia del mapa
  function SetMapRef() {
    const map = useMap();
    useEffect(() => { mapRef.current = map; }, [map]);
    return null;
  }

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      {/* Panel lateral derecho con datos del barrio */}
      {selectedBarrio && (
        <div style={{
          position: 'absolute',
          top: 0,
          right: 0,
          height: '100%',
          width: 340,
          background: '#fff',
          boxShadow: '-2px 0 12px rgba(0,0,0,0.10)',
          zIndex: 2000,
          padding: '32px 28px 24px 28px',
          overflowY: 'auto',
          transition: 'transform 0.3s',
          borderLeft: '1px solid #eee',
          display: 'flex',
          flexDirection: 'column',
        }}>
          <h2 style={{marginTop:0, marginBottom: 18, fontSize: 24, color: '#a50f15'}}>{selectedBarrio}</h2>
          {(() => {
            const data = getSelectedBarrioData();
            if (!data) return <div>No hay datos del barrio.</div>;
            // Variables principales a mostrar primero
            // Variables a excluir
            const excludeVars = ['name', 'D2R_HighCapacity_m', 'D2R_Urban_m'];
            // Todas las variables a mostrar como principales (excepto excluidas)
            const mainVars = Object.keys(data).filter(key => !excludeVars.includes(key));
            // Diccionario de nombres amigables
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
            // Explicaciones para los tooltips
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
            // Función para redondear si es número
            const formatValue = v => {
              const num = Number(v);
              return !isNaN(num) && v !== '' && v !== null ? num.toFixed(2) : v;
            };
            return (
              <>
                <div style={{marginBottom: 18}}>
                  <b style={{fontSize:17, color:'#234567'}}>Indicadores principales</b>
                  <table style={{width:'100%', fontSize:15, borderCollapse:'collapse', marginTop:8, marginBottom:8}}>
                    <tbody>
                      {mainVars.map(key => (
                        <tr key={key}>
                          <td
                            style={{fontWeight:600, padding:'4px 8px 4px 0', color:'#555', cursor:'help'}}
                            title={explanations[key] || ''}
                          >
                            {friendlyNames[key] || key.replace(/_/g,' ')}
                          </td>
                          <td style={{padding:'4px 0'}}>{formatValue(data[key])}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            );
          })()}
        </div>
      )}
      {/* Leyenda de colores abajo a la izquierda */}
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
          {colorLegend.map((item, idx) => (
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
      {error && (
        <div style={{ position: 'absolute', zIndex: 1000, background: '#fff0f0', color: '#b00', padding: 16, border: '1px solid #b00', top: 20, left: '50%', transform: 'translateX(-50%)', maxWidth: 400 }}>
          <b>Ocurrió un error:</b><br />
          {error}
        </div>
      )}
      {selectedBarrio && (
        <button
          onClick={handleVolver}
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
      )}
      <MapContainer center={[37.3886, -5.9823]} zoom={12} style={{ width: '100%', height: '100%' }} whenCreated={map => (mapRef.current = map)}>
        <SetMapRef />
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
        />
        {geojson && !selectedBarrio && (
          <GeoJSON
            data={geojson}
            style={style}
            onEachFeature={(feature, layer) => {
              try {
                  let tempRaw = feature.properties.LST_Target;
                  let tempNum = typeof tempRaw === 'number' ? tempRaw : Number(tempRaw);
                  let tempStr = !isNaN(tempNum) ? tempNum.toFixed(2) : tempRaw;
                  layer.bindTooltip(
                    `${feature.properties.name}<br/>${tempStr} °C`,
                    { sticky: true }
                  );
                layer.on('click', () => handleBarrioClick(feature, layer));
                layer.setStyle({ fillOpacity: 0.7, opacity: 1 });
              } catch (e) {
                setError('Error procesando los datos del barrio');
                console.error('onEachFeature error:', e);
              }
            }}
          />
        )}
        {geojson && selectedBarrio && (
          <GeoJSON
            data={{ ...geojson, features: geojson.features.filter(f => f.properties.name !== selectedBarrio) }}
            style={() => ({ fillColor: '#eee', color: '#bbb', fillOpacity: 0.3, opacity: 0.3, weight: 1, cursor: 'not-allowed' })}
              onEachFeature={(feature, layer) => {
                try {
                  let tempRaw = feature.properties.LST_Target;
                  let tempNum = typeof tempRaw === 'number' ? tempRaw : Number(tempRaw);
                  let tempStr = !isNaN(tempNum) ? tempNum.toFixed(2) : tempRaw;
                  layer.bindTooltip(
                    `${feature.properties.name}<br/>${tempStr} °C`,
                    { sticky: true }
                  );
                  layer.off('click');
                } catch (e) {
                  setError('Error procesando los datos del barrio');
                  console.error('onEachFeature error:', e);
                }
              }}
          />
        )}
        {points.map((p, i) => {
          let lat = parseFloat(p.Latitude);
          let lon = parseFloat(p.Longitude);
          let temp = parseFloat(p.LST_Target);
          if (isNaN(lat) || isNaN(lon) || isNaN(temp)) {
            console.error('Datos inválidos para punto:', p);
            return null;
          }
          return (
            <CircleMarker
              key={i}
              center={[lat, lon]}
              radius={7}
              pathOptions={{ color: getColor(temp), fillColor: getColor(temp), fillOpacity: 0.85, weight: 1 }}
            >
              <Tooltip direction="top" offset={[0, -10]} opacity={1} permanent={false}>
                {`${temp.toFixed(1)} °C`}
              </Tooltip>
            </CircleMarker>
          );
        })}
      </MapContainer>
    </div>
  );
}
