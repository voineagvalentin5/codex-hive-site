(() => {
  'use strict';

  const { planets, replay, cities, missions } = astraData;
  const byId = id => document.getElementById(id);
  const nav = [...document.querySelectorAll('[data-nav]')];
  const sections = [...document.querySelectorAll('#main > .scroll-section')];
  const header = document.querySelector('.topbar');
  const radians = Math.PI / 180;
  const stamp = new Intl.DateTimeFormat('en', {
    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
    hourCycle: 'h23', timeZone: 'UTC',
  });
  const state = { planet: 'earth', spin: 0, step: 0, autoplay: null };

  function formatUTC(value) {
    const date = new Date(value);
    return Number.isFinite(date.getTime()) ? `${stamp.format(date)} UTC` : 'Time unavailable';
  }

  function stars(canvas, seed) {
    const { width, height } = canvas.getBoundingClientRect();
    if (!width || !height) return;
    const pixelRatio = Math.min(devicePixelRatio || 1, 1.6);
    canvas.width = Math.round(width * pixelRatio);
    canvas.height = Math.round(height * pixelRatio);
    const context = canvas.getContext('2d');
    context.scale(pixelRatio, pixelRatio);
    let n = seed;
    function random() {
      n = (Math.imul(n, 1664525) + 1013904223) >>> 0;
      return n / 4294967296;
    }
    const count = Math.min(1100, Math.max(190, Math.floor(width * height / 900)));
    for (let i = 0; i < count; i++) {
      const x = random() * width;
      const y = random() * height;
      const bright = random();
      const radius = bright > .985 ? 1.35 : .25 + random() * .60;
      context.fillStyle = bright > .88 ? '#c0e0ff' : '#aabccf';
      context.globalAlpha = .15 + bright * .67;
      context.beginPath();
      context.arc(x, y, radius, 0, 2 * Math.PI);
      context.fill();
      if (bright > .994) {
        context.globalAlpha = .16;
        context.fillRect(x - 3, y - .35, 6, .7);
        context.fillRect(x - .35, y - 3, .7, 6);
      }
    }
  }

  function paintSphere(canvas, id, options = {}) {
    const width = canvas.getBoundingClientRect().width;
    if (!width) return;
    const size = Math.max(160, Math.min(options.max ?? 650, Math.round(width * Math.min(devicePixelRatio || 1, 1.4))));
    if (canvas.width !== size || canvas.height !== size) canvas.width = canvas.height = size;
    const context = canvas.getContext('2d');
    const center = size / 2;
    const radius = size * (id === 'saturn' ? .265 : .451);
    const color = planets.find(planet => planet.id === id).color;
    const texture = window.AstraGlobe.textures[id];
    const atmosphere = id === 'earth' || id === 'sun' || id === 'neptune' || id === 'uranus';
    context.clearRect(0, 0, size, size);

    if (atmosphere) {
      const glow = context.createRadialGradient(center, center, radius * .95, center, center, size * .49);
      const glowColor = id === 'sun' ? '255, 132, 37' : '91, 179, 255';
      glow.addColorStop(0, `rgba(${glowColor},0)`);
      glow.addColorStop(.42, `rgba(${glowColor},.30)`);
      glow.addColorStop(.68, `rgba(${glowColor},.08)`);
      glow.addColorStop(1, `rgba(${glowColor},0)`);
      context.fillStyle = glow;
      context.fillRect(0, 0, size, size);
    }

    const ring = id === 'saturn' && window.AstraGlobe.ring();
    function drawRings(front) {
      if (!ring) return;
      context.save();
      context.translate(center, center);
      context.rotate(-.29);
      context.scale(1, .34);
      context.beginPath();
      context.rect(-size, front ? 0 : -size, 2 * size, size);
      context.clip();
      const extent = radius * 1.83;
      context.globalAlpha = .86;
      context.drawImage(ring, -extent, -extent, 2 * extent, 2 * extent);
      context.restore();
    }
    drawRings(false);
    if (texture) {
      const image = window.AstraGlobe.render(Math.round(2 * radius), {
        tex: texture,
        spin: options.spin ?? (id === 'earth' ? -1.35 : 0),
        tilt: id === 'saturn' ? -.25 : options.tilt ?? -.17,
        elev: options.elevation ?? .17,
        light: options.light ?? [-.55, .38, .73],
        emissive: id === 'sun',
        ambient: options.ambient ?? .13,
        clouds: id === 'earth' ? window.AstraGlobe.textures.clouds : null,
        night: id === 'earth' ? window.AstraGlobe.textures.night : null,
      });
      context.drawImage(image, center - radius, center - radius, 2 * radius, 2 * radius);
    } else {
      const fill = context.createRadialGradient(center * .65, center * .56, 1, center, center, radius);
      fill.addColorStop(0, color);
      fill.addColorStop(1, '#112033');
      context.fillStyle = fill;
      context.beginPath();
      context.arc(center, center, radius, 0, 2 * Math.PI);
      context.fill();
    }
    if (options.aurora && id === 'earth') paintAurora(context, center, radius, options.elevation);
    drawRings(true);
  }

  function paintAurora(context, center, radius, elevation) {
    context.save();
    context.lineCap = 'round';
    const tilt = -.17;
    context.beginPath();
    context.arc(center, center, radius, 0, 2 * Math.PI);
    context.clip();
    // Soft light along a short viewing arc illustrates the aurora without tracing an observed boundary.
    for (let point = 0; point <= 42; point++) {
      const progress = point / 42;
      const longitude = -1.1 + progress * 2.45;
      const latitude = (64 + 3 * Math.sin(longitude * 5) + 2 * Math.sin(longitude * 9)) * radians;
      const x = Math.cos(latitude) * Math.sin(longitude);
      const y = Math.sin(latitude);
      const z = Math.cos(latitude) * Math.cos(longitude);
      const vertical = y * Math.cos(elevation) - z * Math.sin(elevation);
      const px = center + radius * (x * Math.cos(tilt) - vertical * Math.sin(tilt));
      const py = center - radius * (x * Math.sin(tilt) + vertical * Math.cos(tilt));
      const width = radius * (.035 + .02 * Math.cos(longitude * 9) ** 2);
      const brightness = Math.sin(progress * Math.PI) * .16;
      const light = context.createRadialGradient(px, py, 0, px, py, width);
      light.addColorStop(0, `rgba(126, 240, 184, ${brightness})`);
      light.addColorStop(1, 'rgba(126, 240, 184, 0)');
      context.fillStyle = light;
      context.fillRect(px - width, py - width, 2 * width, 2 * width);
    }
    context.restore();
  }

  const renderers = {
    observatory() {
      stars(byId('hero-stars'), 2280);
      paintSphere(byId('hero-globe'), 'earth', {
        max: 930, spin: -1.33, elevation: .39, tilt: -.32,
        light: [-.76, .31, .58], ambient: .22,
      });
    },
    explore() {
      paintSphere(byId('planet-globe'), state.planet, { spin: state.spin });
    },
    replay() {
      const phase = replay[state.step].phase;
      if (phase === 'transit') paintSphere(byId('transit-sun'), 'sun', { spin: -.45 });
      paintSphere(byId('replay-globe'), phase === 'sun' ? 'sun' : 'earth', {
        spin: [-.5, -1.8, -1.4, -1.31][state.step],
        elevation: phase === 'aurora' ? .55 : .1,
        light: phase === 'aurora' ? [-.9, .27, .24] : [-.6, .36, .66],
        aurora: phase === 'aurora',
      });
    },
    sky() {
      stars(byId('sky-stars'), 610);
    },
  };

  const pendingDraws = new Set();
  let drawFrame = 0;
  function scheduleDraw(section) {
    if (section) pendingDraws.add(section);
    else Object.keys(renderers).forEach(name => pendingDraws.add(name));
    if (drawFrame) return;
    drawFrame = requestAnimationFrame(() => {
      drawFrame = 0;
      pendingDraws.forEach(name => renderers[name]());
      pendingDraws.clear();
    });
  }

  function selectPlanet(id) {
    state.planet = id;
    state.spin = id === 'earth' ? -1.33 : 0;
    const planet = planets.find(value => value.id === id);
    for (const button of byId('planet-menu').children) {
      button.setAttribute('aria-pressed', String(button.dataset.planet === id));
    }
    byId('planet-picker').value = id;
    byId('planet-detail').innerHTML = `
      <p class="eyebrow">${planet.kind}</p>
      <h3 class="detail-title">${planet.name}</h3>
      <p>${planet.text}</p>
      <dl class="fact-row"><div><dt>DIAMETER</dt><dd>${planet.diameter}</dd></div>
        <div><dt>MEAN DISTANCE</dt><dd>${planet.distance}</dd></div></dl>
      <a class="text-link" href="https://science.nasa.gov/${id}/" target="_blank" rel="noopener noreferrer">Explore at NASA ↗</a>`;
    scheduleDraw('explore');
  }

  function setupPlanets() {
    const picker = byId('planet-picker');
    picker.addEventListener('change', () => selectPlanet(picker.value));
    for (const planet of planets) {
      picker.add(new Option(planet.name, planet.id));
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'planet-choice';
      button.dataset.planet = planet.id;
      const dot = document.createElement('span');
      dot.setAttribute('aria-hidden', 'true');
      dot.style.setProperty('--planet-color', planet.color);
      button.append(dot, planet.name);
      button.addEventListener('click', () => selectPlanet(planet.id));
      byId('planet-menu').append(button);
    }
    const canvas = byId('planet-globe');
    let pointer = null;
    canvas.addEventListener('pointerdown', event => {
      if (event.button !== 0 || pointer) return;
      pointer = { id: event.pointerId, x: event.clientX };
      canvas.setPointerCapture(event.pointerId);
    });
    canvas.addEventListener('pointermove', event => {
      if (pointer?.id !== event.pointerId) return;
      state.spin -= (event.clientX - pointer.x) * .012;
      pointer.x = event.clientX;
      scheduleDraw('explore');
    });
    canvas.addEventListener('lostpointercapture', () => { pointer = null; });
    canvas.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
      event.preventDefault();
      state.spin += event.key === 'ArrowLeft' ? .17 : -.17;
      scheduleDraw('explore');
    });
    selectPlanet(state.planet);
  }

  function updateReplay(index) {
    state.step = index;
    byId('share-status').textContent = '';
    const step = replay[index];
    byId('replay-range').value = index;
    byId('replay-range').setAttribute('aria-valuetext', `${step.label}, ${step.date}`);
    byId('step-kind').textContent = step.kind;
    byId('step-title').textContent = step.title;
    byId('step-copy').textContent = step.text;
    byId('step-metric-label').textContent = step.metricLabel;
    byId('step-metric').textContent = step.metric;
    byId('step-date').textContent = step.date;
    byId('step-source').href = step.source;
    byId('replay-scene').dataset.phase = step.phase;
    byId('replay-label').textContent = {
      sun: 'ILLUSTRATION · SUN', transit: 'ILLUSTRATION · SUN TO EARTH',
      earth: 'ILLUSTRATION · EARTH', aurora: 'ILLUSTRATION · AURORA',
    }[step.phase];
    byId('replay-scene-help').textContent = step.phase === 'aurora' ? 'Illustration · Aurora glow is schematic'
      : step.phase === 'transit' ? 'Illustration · Direction from the Sun toward Earth'
      : 'Illustration · Sizes and distances are approximate';
    [...byId('replay-stops').children].forEach((button, position) => {
      button.toggleAttribute('aria-current', position === index);
      if (position === index) button.setAttribute('aria-current', 'step');
    });
    byId('next-step').textContent = index === replay.length - 1 ? 'Restart ↺' : 'Next →';
    scheduleDraw('replay');
  }

  function stopPlayback() {
    if (state.autoplay) clearInterval(state.autoplay);
    state.autoplay = null;
    byId('play-replay').textContent = '▶ Play';
    byId('play-replay').setAttribute('aria-label', 'Play replay');
  }

  function setupReplay() {
    replay.forEach((step, index) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = step.label;
      button.addEventListener('click', () => { stopPlayback(); updateReplay(index); });
      byId('replay-stops').append(button);
    });
    byId('replay-range').max = replay.length - 1;
    byId('replay-range').addEventListener('input', event => {
      stopPlayback();
      updateReplay(Number(event.target.value));
    });
    byId('next-step').addEventListener('click', () => {
      stopPlayback();
      updateReplay((state.step + 1) % replay.length);
    });
    byId('play-replay').addEventListener('click', () => {
      if (state.autoplay) {
        stopPlayback();
        return;
      }
      if (state.step === replay.length - 1) updateReplay(0);
      byId('play-replay').textContent = 'Ⅱ Pause';
      byId('play-replay').setAttribute('aria-label', 'Pause replay');
      state.autoplay = setInterval(() => {
        updateReplay(state.step + 1);
        if (state.step === replay.length - 1) stopPlayback();
      }, 7000);
    });
    byId('share-replay').addEventListener('click', async () => {
      const status = byId('share-status');
      const url = new URL(location.href);
      url.hash = `replay/${replay[state.step].id}`;
      try {
        await navigator.clipboard.writeText(url.href);
        status.textContent = 'Link copied for this replay waypoint.';
      } catch {
        history.replaceState(null, '', url);
        status.textContent = 'Copy the address in your browser to share this waypoint.';
      }
    });
  }

  function solarPosition(date, city) {
    const year = date.getUTCFullYear();
    const day = Math.floor((date - Date.UTC(year, 0, 0)) / 86400000);
    const hours = date.getUTCHours() + date.getUTCMinutes() / 60;
    const daysInYear = (Date.UTC(year + 1, 0, 1) - Date.UTC(year, 0, 1)) / 86400000;
    const gamma = (2 * Math.PI / daysInYear) * (day - 1 + (hours - 12) / 24);
    const equation = 229.18 * (.000075 + .001868 * Math.cos(gamma) - .032077 * Math.sin(gamma)
      - .014615 * Math.cos(2 * gamma) - .040849 * Math.sin(2 * gamma));
    const declination = .006918 - .399912 * Math.cos(gamma) + .070257 * Math.sin(gamma)
      - .006758 * Math.cos(2 * gamma) + .000907 * Math.sin(2 * gamma)
      - .002697 * Math.cos(3 * gamma) + .00148 * Math.sin(3 * gamma);
    const latitude = city.lat * radians;
    const hourAngle = (hours * 15 + equation / 4 + city.lon - 180) * radians;
    const sine = Math.sin(latitude) * Math.sin(declination) + Math.cos(latitude) * Math.cos(declination) * Math.cos(hourAngle);
    const altitude = Math.asin(Math.max(-1, Math.min(1, sine))) / radians;
    const azimuth = (Math.atan2(Math.sin(hourAngle),
      Math.cos(hourAngle) * Math.sin(latitude) - Math.tan(declination) * Math.cos(latitude)) / radians + 540) % 360;
    return { altitude, azimuth };
  }

  function updateSky() {
    const city = cities.find(entry => entry.id === byId('sky-city').value) ?? cities[0];
    const hour = Number(byId('sky-range').value);
    const date = new Date(Date.now() + hour * 3600000);
    const { altitude, azimuth } = solarPosition(date, city);
    const localTime = zone => new Intl.DateTimeFormat(undefined, {
      hour: 'numeric', minute: '2-digit', timeZoneName: 'short', timeZone: zone,
    }).format(date);
    byId('sky-date').textContent = new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeZone: city.zone }).format(date);
    byId('sky-name').textContent = city.name;
    byId('sky-time').textContent = localTime(city.zone);
    byId('sky-altitude').textContent = `${altitude.toFixed(1)}°`;
    byId('sky-condition').textContent = altitude > 0 ? 'The Sun is above the geometric horizon.' : altitude > -18
      ? 'The Sun is below the horizon, within the twilight range.' : 'The Sun is more than 18° below the horizon. The sky is in astronomical night.';
    byId('sky-range').setAttribute('aria-valuetext', hour === 0 ? 'Now' : `${Math.abs(hour)} hours ${hour < 0 ? 'ago' : 'ahead'}`);
    byId('sky-scene').dataset.light = altitude > 0 ? 'day' : altitude > -18 ? 'twilight' : 'night';
    byId('sky-sun').style.top = `${Math.max(12, 69 - altitude * .65)}%`;
    byId('sky-sun').style.left = `${8 + azimuth / 360 * 84}%`;
    byId('sky-sun').hidden = altitude < 0;
    const otherCity = cities.find(entry => entry.id === byId('sky-compare').value);
    const comparison = byId('sky-comparison');
    comparison.hidden = !otherCity;
    if (otherCity) comparison.textContent = `${otherCity.name} · ${localTime(otherCity.zone)} · Sun ${solarPosition(date, otherCity).altitude.toFixed(1)}°`;
    scheduleDraw('sky');
  }

  function setupSky() {
    for (const city of cities) {
      byId('sky-city').add(new Option(city.name, city.id));
      byId('sky-compare').add(new Option(city.name, city.id));
    }
    byId('sky-city').addEventListener('change', updateSky);
    byId('sky-compare').addEventListener('change', updateSky);
    byId('sky-range').addEventListener('input', updateSky);
    byId('sky-now').addEventListener('click', () => { byId('sky-range').value = 0; updateSky(); });
  }

  function setupMissions() {
    byId('mission-grid').innerHTML = missions.map(mission => `
      <article class="mission-card">
        <img src="assets/missions/${mission.image}.webp" loading="lazy" alt="">
        <div><p class="eyebrow">${mission.type}</p><h3>${mission.name}</h3>
          <p>${mission.text}</p>
          <a class="text-link" href="${mission.source}" target="_blank" rel="noopener noreferrer">Mission source ↗</a>
          <small>Image: ${mission.credit}</small></div>
      </article>`).join('');
  }

  function openDeepLink() {
    const [requested, key] = location.hash.slice(1).split('/');
    if (requested === 'about' || (requested === 'learn' && key)) {
      location.replace(`instruments.html${location.hash}`);
      return;
    }
    if (requested === 'signals') {
      history.replaceState(null, '', '#weather');
      byId('weather').scrollIntoView();
      return;
    }
    if (requested === 'explore' && key && planets.some(planet => planet.id === key)) {
      selectPlanet(key);
      byId('explore').scrollIntoView();
    }
    if (requested === 'replay' && key) {
      const matching = replay.findIndex(step => step.id === key);
      if (matching >= 0) {
        stopPlayback();
        updateReplay(matching);
      }
      byId('replay').scrollIntoView();
    }
  }

  let scrollFrame = 0;
  function updateNavigation() {
    scrollFrame = 0;
    const readingLine = header.offsetHeight + Math.min(125, innerHeight * .20);
    const atBottom = document.scrollingElement.scrollHeight - innerHeight - scrollY <= 5;
    const currentSection = atBottom ? sections.at(-1)
      : sections.findLast(section => section.getBoundingClientRect().top <= readingLine) ?? sections[0];
    nav.forEach(link => {
      if (link.dataset.nav === currentSection.id) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  }

  function scheduleNavigation() {
    if (!scrollFrame) scrollFrame = requestAnimationFrame(updateNavigation);
  }

  function setHeaderOffset() {
    document.documentElement.style.setProperty('--nav-height', `${header.offsetHeight}px`);
    scheduleNavigation();
  }

  async function readFeed(url) {
    const response = await fetch(url, { signal: AbortSignal.timeout(8500) });
    if (!response.ok) throw new Error(`Feed status ${response.status}`);
    return response.json();
  }

  async function setSignal(id, request) {
    try {
      const { value, note } = await request();
      byId(`${id}-value`).textContent = value;
      byId(`${id}-note`).textContent = note;
    } catch {
      byId(`${id}-note`).textContent = 'Feed unavailable';
    }
  }

  function loadSignals() {
    setSignal('kp', async () => {
      const data = await readFeed('https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json');
      const last = data.at(-1);
      const time = Array.isArray(last) ? last[0] : last?.time_tag;
      const raw = Array.isArray(last) ? last[1] : last?.Kp ?? last?.kp;
      const value = Number(raw);
      if (!time || raw == null || raw === '' || !Number.isFinite(value)) throw new Error('No measurement');
      const iso = time.includes('Z') || /[+-]\d\d:\d\d$/.test(time) ? time : time.replace(' ', 'T') + 'Z';
      return { value: `Kp ${value.toFixed(1)}`, note: formatUTC(iso) };
    });
    setSignal('flare', async () => {
      const today = new Date();
      const from = new Date(today.getTime() - 6 * 86400000);
      const isoDay = date => date.toISOString().slice(0, 10);
      const flares = await readFeed(`https://ccmc.gsfc.nasa.gov/DONKI-API/get/FLR?startDate=${isoDay(from)}&endDate=${isoDay(today)}`);
      if (!Array.isArray(flares)) throw new Error('Missing flare reports');
      return { value: String(flares.length), note: 'Reported in 7 calendar days' };
    });
    setSignal('iss', async () => {
      const iss = await readFeed('https://api.wheretheiss.at/v1/satellites/25544');
      if (!Number.isFinite(iss.latitude) || !Number.isFinite(iss.timestamp)) throw new Error('Missing position');
      return {
        value: `${Math.abs(iss.latitude).toFixed(1)}°${iss.latitude < 0 ? 'S' : 'N'}`,
        note: formatUTC(iss.timestamp * 1000),
      };
    });
  }

  setupPlanets();
  setupReplay();
  setupSky();
  setupMissions();
  updateReplay(0);
  updateSky();
  byId('open-sources').addEventListener('click', () => byId('sources-dialog').showModal());
  window.addEventListener('hashchange', openDeepLink);
  window.addEventListener('scroll', scheduleNavigation, { passive: true });
  window.addEventListener('resize', () => scheduleDraw());
  new ResizeObserver(setHeaderOffset).observe(header);
  new IntersectionObserver(([entry]) => {
    if (!entry.isIntersecting && state.autoplay) stopPlayback();
  }).observe(byId('replay'));
  setHeaderOffset();
  openDeepLink();
  scheduleDraw();
  window.AstraGlobe.loadAll().then(() => scheduleDraw());
  window.AstraGlobe.loadEarthLayers().then(() => scheduleDraw());
  loadSignals();
})();
