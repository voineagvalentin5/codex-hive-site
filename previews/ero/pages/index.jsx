import React from 'react';
import Head from 'next/head';
import Header from '../components/Header';
import PlanetStatusSidebar from '../components/PlanetStatusSidebar';
import EarthResonanceView from '../components/EarthResonanceView';
import FrequencyLandscape from '../components/FrequencyLandscape';
import ReadingsHistory from '../components/ReadingsHistory';
import TimeAxisControl, { PatternDetection, ContextData, PatternSummary, EventTimeline } from '../components/TimeAxisControl';
import { useStore } from '../stores/useStore';
import { formatUtc, formatDetroit } from '../lib/time';

export default function Home() {
  const { payload, status, error } = useStore();
  const dataTime = payload?.dataTime;
  return (
    <>
      <Head>
        <title>Earth Resonance Observatory</title>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <meta name="description" content="Live NOAA space-weather monitor and the SOS-70 Tomsk Schumann spectrogram. Official 3-hour Kp, solar wind, and GOES flux; Schumann values are reference only." />
        <meta property="og:title" content="Earth Resonance Observatory" />
        <meta property="og:description" content="Live NOAA space-weather monitor and the SOS-70 Tomsk Schumann spectrogram." />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://ero.codex-hive.com/" />
        <meta property="og:image" content="https://ero.codex-hive.com/og-image.jpg" />
        <meta property="og:image:width" content="1200" />
        <meta property="og:image:height" content="630" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="Earth Resonance Observatory" />
        <meta name="twitter:image" content="https://ero.codex-hive.com/og-image.jpg" />
      </Head>
      <main className="observatory-shell">
        <Header />
        <section className="observatory-overview" id="earth" aria-label="Earth and current conditions">
          <EarthResonanceView />
          <div className="overview-readings">
            <PatternDetection />
            <PlanetStatusSidebar />
          </div>
        </section>
        <section className="observatory-section" id="spectrum" aria-labelledby="spectrum-title">
          <header className="section-heading">
            <div>
              <p className="observatory-eyebrow">SOS-70 · Tomsk State University</p>
              <h2 id="spectrum-title">Schumann spectrum</h2>
            </div>
            <p>Explore the 0–40 Hz spectrogram as a heatmap, a 3D surface, or the published source image.</p>
          </header>
          <FrequencyLandscape />
        </section>
        <section className="observatory-section" id="activity" aria-labelledby="activity-title">
          <header className="section-heading">
            <div>
              <p className="observatory-eyebrow">NOAA Space Weather Prediction Center</p>
              <h2 id="activity-title">Solar activity</h2>
            </div>
            <p>Compare recent measurements on a shared time window and review the GOES flare record.</p>
          </header>
          <div className="activity-grid">
            <ContextData />
            <div className="overview-readings">
              <TimeAxisControl />
              <PatternSummary />
            </div>
            <EventTimeline />
          </div>
        </section>
        <div className="observatory-section" id="history">
          <ReadingsHistory />
        </div>
        <footer className="dashboard-footer" id="sources">
          <h2>Data sources</h2>
          <div className="source-list">
            <p><a href="https://www.swpc.noaa.gov/">NOAA SWPC</a> · Kp, solar wind, GOES flux and the OVATION forecast.</p>
            <p><a href="https://sos70.ru/">SOS-70, Tomsk State University</a> · Published Schumann spectrogram.</p>
            <p>Lightning rate · No live feed.</p>
          </div>
          <p className="footer-status">
            NOAA checks every 60 seconds. Last observation {dataTime ? `${formatUtc(dataTime, { seconds: false })} · ${formatDetroit(dataTime, { seconds: false })}` : 'unavailable'}.
            {error && <span className="feed-error">{status === 'stale' ? 'Showing last available readings' : 'NOAA readings unavailable'} · {error}</span>}
          </p>
        </footer>
      </main>
    </>
  );
}
