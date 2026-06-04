import React from 'react';
import InfoHoverIcon from './InfoHoverIcon';

const explanations = {
  NDVI: {
    title: 'Indice de Vegetacion (NDVI)',
    subtitle: 'La cantidad de vida vegetal viva y sana.',
    summary: 'Mide la densidad de plantas y hojas verdes visibles en superficie.',
    points: [
      { label: 'Si lo aumentas', text: 'Simulas mas cobertura vegetal y refrescas por evapotranspiracion.' },
      { label: 'Si lo disminuyes', text: 'Simulas sequia, tala o sustitucion de verde por suelo seco.' }
    ]
  },
  NDBI: {
    title: 'Indice de Construccion (NDBI)',
    subtitle: 'La huella del asfalto, hormigon y ladrillo.',
    summary: 'Representa cuanto suelo natural ha sido sellado por materiales artificiales.',
    points: [
      { label: 'Si lo aumentas', text: 'Mas pavimento y masa construida; sube la acumulacion de calor.' },
      { label: 'Si lo disminuyes', text: 'Simulas levantar pavimento y recuperar suelo natural.' }
    ]
  },
  Albedo: {
    title: 'Reflectancia Solar (Albedo)',
    subtitle: 'El color de la ciudad frente al sol.',
    summary: 'Mide cuanta radiacion se refleja al cielo en vez de absorberse en superficie.',
    points: [
      { label: 'Si lo aumentas', text: 'Simulas cubiertas y pavimentos claros; enfriamiento mas inmediato.' },
      { label: 'Si lo disminuyes', text: 'Simulas superficies oscuras que retienen mayor carga termica.' }
    ]
  },
  D2W_meters: {
    title: 'Distancia al Agua',
    subtitle: 'La influencia del rio Guadalquivir.',
    summary: 'Indica a cuantos metros esta el punto de la principal masa de agua urbana.',
    points: [
      { label: 'Si lo aumentas', text: 'Simulas alejarte del rio: menos brisa y menor efecto termorregulador.' },
      { label: 'Si lo disminuyes', text: 'Simulas acercarte a la orilla: maximas mas suaves por humedad y corrientes.' },
      { label: 'Nota', text: 'En este simulador es un control hipotetico.' }
    ]
  },
  LST_Target: {
    title: 'Temperatura de Superficie',
    summary: 'Valor medio estimado de temperatura superficial para el barrio.'
  },
  Tree_Density_50m: {
    title: 'Densidad de Arboles',
    subtitle: 'El escudo de sombra a pie de calle.',
    summary: 'Cuenta arboles de copa en el entorno cercano (radio de 50 m).',
    points: [
      { label: 'Si lo aumentas', text: 'Mas sombra directa en calles y plazas; baja la temperatura percibida.' },
      { label: 'Si lo disminuyes', text: 'Simulas poda extrema o tala del arbolado urbano.' }
    ]
  },
  Building_Density_100m: {
    title: 'Densidad de Edificios',
    subtitle: 'Lo apretados que estan los bloques.',
    summary: 'Mide la ocupacion del suelo por edificios frente a espacio libre.',
    points: [
      { label: 'Si lo aumentas', text: 'Puede atrapar calor nocturno pero tambien crear sombra diurna.' },
      { label: 'Si lo disminuyes', text: 'Mas apertura urbana y mas exposicion solar directa.' }
    ]
  },
  Avg_Building_Height_100m: {
    title: 'Altura Media de Edificios',
    subtitle: 'El perfil vertical del barrio.',
    summary: 'Indica la altura media de las construcciones cercanas.',
    points: [
      { label: 'Si lo aumentas', text: 'Sombras mas largas, pero posible bloqueo de ventilacion.' },
      { label: 'Si lo disminuyes', text: 'Entorno de baja altura con mayor impacto solar sobre suelo y cubiertas.' }
    ]
  },
};

export default function SidePanelDetailedSection({
  mainVars,
  defaultValues,
  modifiedValues,
  friendlyNames,
  formatValue,
  getRangeForKey,
  getPercentChange,
  handleSliderChange,
  onReset,
}) {
  return (
    <div style={{ marginBottom: 18 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <b style={{ fontSize: 18, color: '#234567' }}>Indicadores principales</b>
        <button onClick={onReset} style={{ background: 'transparent', border: 'none', color: '#2b6cb0', cursor: 'pointer', fontSize: 13 }}>restablecer</button>
      </div>
      <table style={{ width: '100%', fontSize: 16, borderCollapse: 'collapse', marginTop: 8, marginBottom: 8 }}>
        <tbody>
          {mainVars.map(key => {
            const def = defaultValues[key];
            const mod = modifiedValues[key];
            const current = mod !== undefined ? mod : def;
            const range = getRangeForKey(key, def);
            const isNumeric = range !== null;
            return (
              <tr key={key} style={{ verticalAlign: 'middle' }}>
                <td style={{ fontWeight: 600, padding: '6px 10px 6px 0', color: '#555', width: '40%' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ textAlign: 'left' }}>{friendlyNames[key] || key.replace(/_/g, ' ')}</span>
                    <InfoHoverIcon text={explanations[key] || ''} />
                  </div>
                </td>
                <td style={{ padding: '4px 0', width: '60%' }}>
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
  );
}
