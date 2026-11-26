import React, { useCallback, useState } from 'react';
import dynamic from 'next/dynamic';
import HudPanel from './HudPanel';

const Globe = dynamic(() => import('./Globe'), { ssr: false });

export default function EarthResonanceView() {
  const [ready, setReady] = useState(false);
  const showGlobe = useCallback(() => setReady(true), []);

  return (
    <HudPanel title="Earth view" className="earth-panel">
      <figure className="earth-figure">
        <div className="space-field" aria-hidden="true">
          <div className="earth-orbit" />
          {!ready && <img className="earth-fallback" src="/textures/earth-epic.webp" width="640" height="640" alt="" fetchPriority="high" />}
          <div className={`globe-wrap ${ready ? 'ready' : ''}`}><Globe onReady={showGlobe} /></div>
        </div>
        <figcaption className="globe-credit">
          <strong>{ready ? 'Computed day / night' : 'Earth photograph'}</strong>
          <span>{ready ? 'NASA Blue Marble and night lights · not a live image' : 'NASA DSCOVR / EPIC · November 22, 2026'}</span>
        </figcaption>
      </figure>
    </HudPanel>
  );
}
