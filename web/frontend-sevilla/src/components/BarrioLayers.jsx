import React from 'react';
import { GeoJSON } from 'react-leaflet';

export default function BarrioLayers({ geojson, selectedBarrio, style, onBarrioClick, setError }) {
  if (!geojson) return null;

  return (
    <>
      {!selectedBarrio && (
        <GeoJSON
          data={geojson}
          style={style}
          onEachFeature={(feature, layer) => {
            try {
              let tempRaw = feature.properties.LST_Target;
              let tempNum = typeof tempRaw === 'number' ? tempRaw : Number(tempRaw);
              let tempStr = !isNaN(tempNum) ? tempNum.toFixed(2) : tempRaw;
              layer.bindTooltip(`${feature.properties.name}<br/>${tempStr} °C`, { sticky: true });
              layer.on('click', () => onBarrioClick(feature, layer));
              layer.setStyle({ fillOpacity: 0.7, opacity: 1 });
            } catch (e) {
              setError && setError('Error procesando los datos del barrio');
              console.error('onEachFeature error:', e);
            }
          }}
        />
      )}

      {selectedBarrio && (
        <GeoJSON
          data={{ ...geojson, features: geojson.features.filter(f => f.properties.name !== selectedBarrio) }}
          style={() => ({ fillColor: '#eee', color: '#bbb', fillOpacity: 0.3, opacity: 0.3, weight: 1, cursor: 'not-allowed' })}
          onEachFeature={(feature, layer) => {
            try {
              let tempRaw = feature.properties.LST_Target;
              let tempNum = typeof tempRaw === 'number' ? tempRaw : Number(tempRaw);
              let tempStr = !isNaN(tempNum) ? tempNum.toFixed(2) : tempRaw;
              layer.bindTooltip(`${feature.properties.name}<br/>${tempStr} °C`, { sticky: true });
              layer.off('click');
            } catch (e) {
              setError && setError('Error procesando los datos del barrio');
              console.error('onEachFeature error:', e);
            }
          }}
        />
      )}
    </>
  );
}
