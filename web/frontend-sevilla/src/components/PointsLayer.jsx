import React from 'react';
import { CircleMarker, Tooltip } from 'react-leaflet';

export default function PointsLayer({ points, getColor }) {
  if (!points || points.length === 0) return null;
  return (
    <>
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
    </>
  );
}
