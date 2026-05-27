export const colorLegend = [
  { label: '≥ 50°C', color: '#67000d' },
  { label: '47–49.9°C', color: '#b30000' },
  { label: '44–46.9°C', color: '#e34a33' },
  { label: '41–43.9°C', color: '#f39c12' },
  { label: '38–40.9°C', color: '#ffd966' },
  { label: '35–37.9°C', color: '#7bd389' },
  { label: '< 35°C', color: '#2ecc71' },
];

export function getColor(temp) {
  return temp >= 50 ? '#67000d'
    : temp >= 47 ? '#b30000'
    : temp >= 44 ? '#e34a33'
    : temp >= 41 ? '#f39c12'
    : temp >= 38 ? '#ffd966'
    : temp >= 35 ? '#7bd389'
    : '#2ecc71';
}

export const barrioStyle = feature => ({
  fillColor: getColor(feature.properties.LST_Target),
  weight: 1,
  opacity: 1,
  color: '#234567',
  fillOpacity: 0.7,
  cursor: 'pointer',
});

export function parseCSV(text) {
  const lines = text.trim().split('\n');
  const headers = lines[0].split(',');
  return lines.slice(1).map(line => {
    const values = line.split(',');
    const obj = {};
    headers.forEach((h, i) => obj[h] = values[i]);
    return obj;
  });
}
