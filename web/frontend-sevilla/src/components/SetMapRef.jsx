import React, { useEffect } from 'react';
import { useMap } from 'react-leaflet';

export default function SetMapRef({ mapRef }) {
  const map = useMap();
  useEffect(() => { if (mapRef) mapRef.current = map; }, [map, mapRef]);
  return null;
}
