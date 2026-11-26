import React from 'react';
import { useStore } from '../stores/useStore';
import HudPanel from './HudPanel';
import LiveValue from './LiveValue';
import { fmt, signed, fmtTemp } from '../lib/format';

export default function PlanetStatusSidebar() {
  const payload = useStore((state) => state.payload);
  const latest = payload?.latest || {};
  const classification = payload?.classification;
  const wind = latest.solarWind || {};
  const rows = [
    { label: 'Estimated Kp', detail: 'NOAA 1-minute index', raw: latest.kpEstimated?.value, value: fmt(latest.kpEstimated?.value, 2) },
    { label: 'Official Kp', detail: 'NOAA 3-hour index', raw: latest.kpOfficial?.value, value: fmt(latest.kpOfficial?.value, 2) },
    { label: 'Solar wind speed', detail: classification?.solarWindSpeed?.label || 'Propagated solar wind', raw: wind.speed, value: fmt(wind.speed, 0), unit: 'km/s' },
    { label: 'Solar wind density', raw: wind.density, value: fmt(wind.density, 2), unit: 'p/cm³' },
    { label: 'Solar wind temperature', raw: wind.temperature, value: fmtTemp(wind.temperature) },
    { label: 'Magnetic field Bz', detail: classification?.bz?.label || 'IMF Bz (GSM)', raw: wind.bz, value: signed(wind.bz, 1), unit: 'nT' },
    { label: 'Magnetic field strength', detail: 'Total IMF', raw: wind.bt, value: fmt(wind.bt, 1), unit: 'nT' },
    { label: 'OVATION peak', detail: 'Aurora forecast grid maximum', raw: latest.aurora?.maxIntensity, value: fmt(latest.aurora?.maxIntensity, 0) },
  ];

  return (
    <HudPanel title="Planet readings" className="left-panel">
      <dl className="planet-readings">
        {rows.map(({ label, detail, raw, value, unit }) => (
          <div className="metric-row" key={label}>
            <dt>{label}{detail && <small>{detail}</small>}</dt>
            <dd>
              <LiveValue value={raw}>{value}{unit && value !== '—' && <small>{unit}</small>}</LiveValue>
            </dd>
          </div>
        ))}
      </dl>
    </HudPanel>
  );
}
