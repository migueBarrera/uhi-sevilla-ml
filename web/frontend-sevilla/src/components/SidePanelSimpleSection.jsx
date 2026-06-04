import React from 'react';
import InfoHoverIcon from './InfoHoverIcon';

const simpleExplanations = {
  reforestation: {
    title: 'Plan de Reforestacion y Zonas Verdes',
    subtitle: 'Transforma el asfalto en naturaleza.',
    summary: 'Simula levantar pavimento para crear parques, jardines y plantar nuevos arboles en el barrio.',
    points: [
      { label: 'Si lo aumentas', text: 'Baja la temperatura: hay mas sombra y evapotranspiracion natural.' },
      { label: 'Ejemplo real', text: 'Convertir un aparcamiento asfaltado o una calle dura en un bulevar arbolado.' },
      { label: 'Si esta a cero', text: 'El barrio se mantiene con el arbolado y parques actuales.' }
    ]
  },
  densification: {
    title: 'Densidad y Desarrollo Urbano',
    subtitle: 'Anade nuevos edificios o esponja el barrio.',
    summary: 'Modifica tanto el suelo ocupado por construccion como la altura media de los edificios.',
    points: [
      { label: 'Si lo aumentas', text: 'Sube la temperatura por mas hormigon y menos suelo natural.' },
      { label: 'Ejemplo real', text: 'Construir en solares vacios o anadir plantas a edificios existentes.' },
      { label: 'Si lo disminuyes', text: 'Mejora la ventilacion y se reduce el calor atrapado durante la noche.' }
    ]
  },
  coolRoofs: {
    title: 'Materiales Reflectantes (Cool Roofs)',
    subtitle: 'Pinta los tejados de blanco para combatir el sol.',
    summary: 'Simula aumentar reflectancia solar sin cambiar la forma urbana ni el numero de arboles.',
    points: [
      { label: 'Si lo aumentas', text: 'Baja la temperatura al reflejar mas radiacion solar.' },
      { label: 'Ejemplo real', text: 'Azoteas blancas, cubiertas frias y pavimentos de color claro.' }
    ]
  }
};

export default function SidePanelSimpleSection({
  scenarioControls,
  onScenarioControlChange,
  onReset,
}) {
  return (
    <div style={{ marginBottom: 18 }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <b style={{ fontSize: 18, color: '#234567' }}>Balancines de escenario</b>
        <button onClick={onReset} style={{ background: 'transparent', border: 'none', color: '#2b6cb0', cursor: 'pointer', fontSize: 13 }}>restablecer</button>
      </div>

      <div style={{ marginTop: 12, padding: 10, border: '1px solid #eef2f8', borderRadius: 10, background: '#fbfcff' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
          <div style={{ display: 'flex', alignItems: 'center', fontSize: 14, fontWeight: 600, color: '#425466' }}>
            Reforestacion
            <InfoHoverIcon text={simpleExplanations.reforestation} />
          </div>
          <div style={{ fontWeight: 700, color: '#2b6cb0' }}>{scenarioControls.reforestation}</div>
        </div>
        <input
          type="range"
          min={0}
          max={100}
          step={1}
          value={scenarioControls.reforestation}
          onChange={e => onScenarioControlChange('reforestation', e.target.value)}
          style={{ width: '100%' }}
        />
      </div>

      <div style={{ marginTop: 10, padding: 10, border: '1px solid #eef2f8', borderRadius: 10, background: '#fbfcff' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
          <div style={{ display: 'flex', alignItems: 'center', fontSize: 14, fontWeight: 600, color: '#425466' }}>
            Densificacion urbana
            <InfoHoverIcon text={simpleExplanations.densification} />
          </div>
          <div style={{ fontWeight: 700, color: '#2b6cb0' }}>{scenarioControls.densification}</div>
        </div>
        <input
          type="range"
          min={-50}
          max={100}
          step={1}
          value={scenarioControls.densification}
          onChange={e => onScenarioControlChange('densification', e.target.value)}
          style={{ width: '100%' }}
        />
      </div>

      <div style={{ marginTop: 10, padding: 10, border: '1px solid #eef2f8', borderRadius: 10, background: '#fbfcff' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
          <div style={{ display: 'flex', alignItems: 'center', fontSize: 14, fontWeight: 600, color: '#425466' }}>
            Cool roofs / materiales reflectantes
            <InfoHoverIcon text={simpleExplanations.coolRoofs} />
          </div>
          <div style={{ fontWeight: 700, color: '#2b6cb0' }}>{scenarioControls.coolRoofs}</div>
        </div>
        <input
          type="range"
          min={0}
          max={100}
          step={1}
          value={scenarioControls.coolRoofs}
          onChange={e => onScenarioControlChange('coolRoofs', e.target.value)}
          style={{ width: '100%' }}
        />
      </div>
    </div>
  );
}
