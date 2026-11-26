import React, { useEffect, useMemo, useState } from 'react';
import dynamic from 'next/dynamic';
import HudPanel from './HudPanel';
import { useStore } from '../stores/useStore';
import { sampleSpectrogram, referenceModel } from '../lib/spectrogram';
import { STATIC_SITE } from '../lib/swpc';

const Spectrogram3D = dynamic(() => import('./Spectrogram3D'), { ssr: false });
const Spectrogram2D = dynamic(() => import('./Spectrogram2D'), { ssr: false });

export default function FrequencyLandscape() {
  const { payload } = useStore();
  const refs = useMemo(() => payload?.schumann?.referenceHz || [7.83, 14.3, 20.8, 27.3, 33.8], [payload?.schumann?.referenceHz?.join(',')]);
  const labels = useMemo(() => payload?.schumann?.referenceLabels || ['Fund.', '2nd', '3rd', '4th', '5th'], [payload?.schumann?.referenceLabels?.join(',')]);
  const spec = payload?.schumann?.spectrogram;
  const [view, setView] = useState('2d'); // 2D pane only: heatmap | source image
  const [grid, setGrid] = useState(null);
  const [state, setState] = useState('loading'); // loading | image | model
  const [publishedImage, setPublishedImage] = useState(null);
  // Re-sample at most every 10 minutes; the source image updates slowly.
  const [bucket, setBucket] = useState(() => Math.floor(Date.now() / 600000));
  useEffect(() => {
    const id = setInterval(() => setBucket(Math.floor(Date.now() / 600000)), 60000);
    return () => clearInterval(id);
  }, []);
  // Static site: the image is a same-origin snapshot written by a scheduled
  // GitHub Action, with a small JSON file saying when (and whether) it was fetched.
  const metaUrl = STATIC_SITE ? '/data/shm-meta.json' : null;
  const [meta, setMeta] = useState(metaUrl ? null : { ok: true });
  useEffect(() => {
    if (!metaUrl) { setMeta({ ok: true }); return undefined; }
    let alive = true;
    fetch(`${metaUrl}?b=${bucket}`, { cache: 'no-cache' })
      .then((r) => (r.ok ? r.json() : { ok: false }))
      .then((m) => { if (alive) setMeta(m && typeof m === 'object' ? m : { ok: false }); })
      .catch(() => { if (alive) setMeta({ ok: false }); });
    return () => { alive = false; };
  }, [metaUrl, bucket]);
  const feedDown = !!meta && meta.ok === false;
  const proxyUrl = spec?.proxyUrl || (STATIC_SITE ? '/data/shm.jpg' : '/api/schumann-spectrogram');
  const src = meta && !feedDown ? `${proxyUrl}?b=${bucket}` : null;
  const fetchedLabel = meta?.fetchedAt ? fmtUtc(meta.fetchedAt) : null;

  useEffect(() => {
    if (metaUrl && !meta) return undefined;
    if (!src) { setGrid(referenceModel(refs)); setState('model'); return undefined; }
    let alive = true;
    const img = new Image();
    img.decoding = 'async';
    img.onload = () => {
      if (!alive) return;
      setPublishedImage(src);
      try {
        const g = sampleSpectrogram(img);
        if (g.ok) { setGrid(g); setState('image'); } else { setGrid(referenceModel(refs)); setState('model'); }
      } catch (e) { setGrid(referenceModel(refs)); setState('model'); }
    };
    img.onerror = () => { if (alive) { setGrid(referenceModel(refs)); setState('model'); } };
    img.src = src;
    return () => { alive = false; };
  }, [src, refs, metaUrl, !!meta]);

  const timeLabels = useMemo(() => (state === 'image' ? ['older', 'newest'] : null), [state]);
  const credit = `Source: ${spec?.credit || 'Space Observing System (SOS-70), Tomsk State University'} · ${spec?.pageUrl || 'https://sos70.ru/'} · image only, no numeric API`;
  const badgeClass = `spec-badge ${state === 'model' ? 'warn' : ''}`;
  const sourceLine = ' · Source: SOS-70, Tomsk State University (sos70.ru)';

  const honesty = () => {
    if (state === 'image') {
      return <><b>Relative intensity, not calibrated dB</b> · derived from the SOS-70 Tomsk spectrogram image (0–40 Hz, about 3 days){fetchedLabel ? <> · image fetched {fetchedLabel}</> : null} · dashed lines = textbook harmonics, reference only</>;
    }
    if (state === 'model') {
      return <>{feedDown ? <><b>Tomsk feed unavailable</b> · </> : null}<b>Reference model, not live</b> · textbook harmonics only, no measured amplitude</>;
    }
    return <>Loading SOS-70 spectrogram…</>;
  };

  return (
    <>
    <div className="landscape-pair">
      <HudPanel title="Spectrogram" className="spec2d-panel">
        <div className="panel-tools">
          <div className="seg small">
            <button aria-pressed={view === '2d'} className={view === '2d' ? 'active' : ''} onClick={() => setView('2d')}>2D heatmap</button>
            <button aria-pressed={view === 'img'} className={view === 'img' ? 'active' : ''} onClick={() => setView('img')}>Source image</button>
          </div>
        </div>
        <div className="spec2d-body">
          {view === '2d' ? (
            grid ? <Spectrogram2D data={grid} refs={refs} labels={labels} timeLabels={timeLabels} state={state} /> : <div className="spec-loading">Loading SOS-70 spectrogram…</div>
          ) : src && publishedImage === src ? (
            <img className="spec-img" src={src} alt="Latest public Schumann spectrogram from SOS-70, Tomsk State University" />
          ) : <div className="spec-loading">{state === 'loading' ? 'Loading source image…' : 'Source image unavailable.'}</div>}
        </div>
        <p className={badgeClass} title={credit}>
          {view === '2d' && honesty()}
          {view === 'img' && (state !== 'loading' && (!src || publishedImage !== src)
            ? <><b>Tomsk feed unavailable</b> · the published SOS-70 image could not be displayed</>
            : <>SOS-70 spectrogram as published (0–40 Hz, about 3 days){fetchedLabel ? <> · fetched {fetchedLabel}</> : null} · image only, no numeric API</>)}
          {sourceLine}
        </p>
      </HudPanel>

      <HudPanel title="Frequency landscape" className="landscape-panel" aside={<span className="aside-live">3D surface</span>}>
        <div className="landscape-body">
          {grid ? <Spectrogram3D data={grid} refs={refs} timeLabels={timeLabels} /> : <div className="spec-loading">Loading SOS-70 spectrogram…</div>}
          {grid ? (
            <div className="spec-key" aria-hidden="true">
              <span>low</span><i /><span>high</span>
              <em>{state === 'model' ? 'model shape only' : 'relative intensity (image colour bar)'}</em>
            </div>
          ) : null}
          {grid ? <span className="orbit-hint">drag to orbit · double-click to reset</span> : null}
        </div>
        <p className={badgeClass} title={credit}>
          {honesty()}
          {sourceLine}
        </p>
      </HudPanel>
    </div>
    <div className="harmonic-reference">
      <div><strong>Schumann harmonics</strong><p>Textbook reference frequencies</p></div>
      <ul aria-label="Reference frequencies">
        {refs.map((hz, i) => <li key={hz}><small>{i === 0 ? 'Fundamental' : `${i + 1} · Harmonic`}</small><b>{hz.toFixed(2)} Hz</b></li>)}
      </ul>
    </div>
    </>
  );
}

function fmtUtc(iso) {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return null;
  const p = (n) => String(n).padStart(2, '0');
  return `${d.getUTCDate()} ${['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][d.getUTCMonth()]} ${p(d.getUTCHours())}:${p(d.getUTCMinutes())} UTC`;
}
