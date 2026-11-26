import React, { useEffect, useState } from 'react';
import { useStore } from '../stores/useStore';
import { formatUtc, formatDetroit } from '../lib/time';

export default function Header() {
  const { payload, status, fetchedAt } = useStore();
  const [now, setNow] = useState(null);
  useEffect(() => {
    setNow(new Date());
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  const dataTime = payload?.dataTime;
  const loading = status === 'idle' || status === 'loading';
  const counts = payload?.feedStatus;
  const partial = status === 'live' && counts && counts.ok < counts.total;
  const live = status === 'live' && !partial;
  const feedLabel = live ? 'NOAA online' : partial ? 'Partial NOAA feeds' : loading ? 'Connecting to NOAA' : status === 'stale' ? 'NOAA readings stale' : 'NOAA unavailable';

  return (
    <header className="dashboard-header">
      <div className="dashboard-masthead">
        <div className="brand-block">
          <div className="brand-identity">
            <img src="/brand/ero-emblem.webp" width="46" height="46" alt="" />
            <p className="observatory-eyebrow">Codex Hive Research</p>
          </div>
          <h1>Earth Resonance <em>Observatory</em></h1>
          <p className="observatory-deck">Live space weather from NOAA and the Schumann spectrum from Tomsk.</p>
        </div>
        <div className="header-console">
          <div className="clock-block">
            <strong>{now ? now.toLocaleTimeString('en-GB', { timeZone: 'UTC', hour12: false }) : '--:--:--'} <small>UTC</small></strong>
            <span>{now ? formatDetroit(now, { seconds: false }) : 'America/Detroit'}</span>
          </div>
          <div className="feed-block">
            <span className={`live-block ${live ? 'is-live' : 'is-off'}`} role="status">
              <i aria-hidden="true" />{feedLabel}{counts && !loading && <small>{counts.ok}/{counts.total}</small>}
            </span>
            <span>{dataTime ? `Last data ${formatUtc(dataTime, { seconds: false }).replace(/ \d{4} /, ' ')}` : fetchedAt ? 'Observation time unavailable' : 'Waiting for first observation'}</span>
          </div>
        </div>
      </div>
      <nav className="observatory-nav" aria-label="Observatory sections">
        <a href="#earth">Earth view</a>
        <a href="#spectrum">Schumann spectrum</a>
        <a href="#activity">Solar activity</a>
        <a href="#history">Readings history</a>
      </nav>
    </header>
  );
}
