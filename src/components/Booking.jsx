import { useState, useEffect, useRef } from 'react';

const IG = 'https://www.instagram.com/mehndi_by_manna_/';
const SERVICES = [
  { id: 'bridal', name: 'Bridal Henna', note: 'Listed on the Instagram profile' },
  { id: 'nonbridal', name: 'Non-Bridal Henna', note: 'Listed on the Instagram profile' },
  { id: 'guest', name: 'Guest Henna', note: 'Illustrative option, for this demonstration only' },
];
const SLOTS = [['Morning', '9:00 AM'], ['Morning', '11:00 AM'], ['Afternoon', '2:00 PM'], ['Afternoon', '4:00 PM'], ['Evening', '6:00 PM']];
const EVENTS = ['Wedding', 'Engagement', 'Festival', 'Other occasion'];
const LABELS = ['Service', 'Date', 'Time', 'Details', 'Review'];
const START = new Date(2026, 9, 19), END = new Date(2026, 11, 31);
const pad = (n) => String(n).padStart(2, '0');
const key = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
const parse = (k) => { const [y, m, d] = k.split('-').map(Number); return new Date(y, m - 1, d); };
const DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const long = (d) => `${DAYS[d.getDay()]} ${d.getDate()} ${MONTHS[d.getMonth()]} ${d.getFullYear()}`;
// Deterministic SAMPLE availability: pure illustration, not real data.
const status = (d) => { const h = (d.getDate() * 3 + d.getMonth()) % 5; return h === 0 ? 'full' : h === 1 ? 'limited' : 'open'; };
const slotOpen = (d, i) => status(d) !== 'full' && (d.getDate() + i) % 4 !== 0;
const inWin = (d) => d >= START && d <= END;
const word = { open: 'sample: available', limited: 'sample: limited', full: 'sample: unavailable' };
const fresh = () => ({ service: 'guest', date: '2026-10-23', time: null, form: { name: '', event: '', guests: '2', notes: '' } });

function validate(f) {
  const e = {};
  if (f.name.trim().length < 2) e.name = 'Enter a name or nickname of at least 2 characters. A made-up name is fine for this demo.';
  if (!f.event) e.event = 'Choose an occasion type.';
  const g = Number(f.guests);
  if (!f.guests || !Number.isInteger(g) || g < 1 || g > 50) e.guests = 'Guest count must be a whole number from 1 to 50.';
  if (f.notes.length > 300) e.notes = 'Please keep notes to 300 characters or fewer.';
  return e;
}

export default function Booking() {
  const [step, setStep] = useState(0);
  const [s, setS] = useState(fresh);
  const [errs, setErrs] = useState({});
  const [msg, setMsg] = useState('');
  const [ref, setRef] = useState('');
  const [note, setNote] = useState('');
  const [month, setMonth] = useState(new Date(2026, 9, 1));
  const [fd, setFd] = useState('2026-10-23');
  const head = useRef(null), first = useRef(true), cal = useRef(null), focusCal = useRef(false), strip = useRef(null);
  const date = parse(s.date), svc = SERVICES.find((x) => x.id === s.service);

  useEffect(() => { if (first.current) { first.current = false; return; } head.current?.focus(); }, [step]);
  useEffect(() => {
    const pick = (id) => SERVICES.some((x) => x.id === id) && setS((p) => ({ ...p, service: id }));
    if (window.__demoService) pick(window.__demoService);
    const h = (e) => { pick(e.detail); setStep(0); setMsg(''); };
    window.addEventListener('demo-service', h);
    return () => window.removeEventListener('demo-service', h);
  }, []);
  useEffect(() => {
    if (step === 1 && strip.current) { const c = strip.current.querySelector('[aria-pressed=true]'); if (c) strip.current.scrollLeft += c.getBoundingClientRect().left - strip.current.getBoundingClientRect().left - 8; }
  }, [step]);
  useEffect(() => { if (focusCal.current) { cal.current?.querySelector(`[data-k="${fd}"]`)?.focus(); focusCal.current = false; } }, [fd, month]);

  const pickDate = (k) => {
    const d = parse(k);
    if (!inWin(d) || status(d) === 'full') return;
    setNote(s.time !== null && k !== s.date ? 'Your time was cleared because sample slots differ by date. You can choose a new one on the next step.' : '');
    setS((p) => ({ ...p, date: k, time: k === p.date ? p.time : null }));
    setFd(k); setMsg('');
  };
  const goMonth = (n) => {
    const m = new Date(month.getFullYear(), month.getMonth() + n, 1); setMonth(m);
    const sd = parse(s.date); setFd(key(sd.getMonth() === m.getMonth() && sd.getFullYear() === m.getFullYear() ? sd : m < START ? START : m));
  };
  const calKeys = (e) => {
    const map = { ArrowLeft: -1, ArrowRight: 1, ArrowUp: -7, ArrowDown: 7 };
    let nd = parse(fd);
    if (e.key in map) nd.setDate(nd.getDate() + map[e.key]);
    else if (e.key === 'PageDown' || e.key === 'PageUp') { const t = new Date(nd.getFullYear(), nd.getMonth() + (e.key === 'PageDown' ? 1 : -1), 1); t.setDate(Math.min(nd.getDate(), new Date(t.getFullYear(), t.getMonth() + 1, 0).getDate())); nd = t; }
    else return;
    e.preventDefault();
    if (nd < START) nd = START; if (nd > END) nd = END;
    focusCal.current = true; setFd(key(nd)); setMonth(new Date(nd.getFullYear(), nd.getMonth(), 1));
  };
  const setF = (k, v) => setS((p) => ({ ...p, form: { ...p.form, [k]: v } }));
  const adj = (n) => setF('guests', String(Math.min(50, Math.max(1, (parseInt(s.form.guests, 10) || 0) + n))));
  const next = () => {
    if (step === 2 && s.time === null) { setMsg('Please choose a sample time slot to continue.'); return; }
    if (step === 3) { const e = validate(s.form); setErrs(e); if (Object.keys(e).length) { setMsg('Please fix the highlighted fields.'); const f = ['name', 'event', 'guests', 'notes'].find((x) => e[x]); setTimeout(() => document.getElementById('f-' + f)?.focus(), 0); return; } }
    setMsg(''); setStep(step + 1);
  };
  const submit = () => { setRef('DEMO-' + Math.random().toString(36).slice(2, 8).toUpperCase()); setStep(5); };
  const reset = () => { setS(fresh()); setStep(0); setErrs({}); setMsg(''); setNote(''); setRef(''); setMonth(new Date(2026, 9, 1)); setFd('2026-10-23'); window.__demoService = undefined; };

  const timeTxt = s.time === null ? null : `${SLOTS[s.time][1]} (${SLOTS[s.time][0].toLowerCase()}, sample slot)`;
  const sum = [['Service', svc.name], ['Date', long(date) + ' (sample date)'], ['Time', timeTxt]];
  const H = ({ n, children }) => <h3 ref={head} tabIndex={-1}><small>Step {n} of 5</small>{children}</h3>;
  const Err = ({ id }) => errs[id] ? <p className="err" id={`e-${id}`}>{errs[id]}</p> : null;
  const inv = (id) => ({ 'aria-invalid': !!errs[id], 'aria-describedby': errs[id] ? `e-${id}` : undefined });

  const weeks = []; {
    const first1 = new Date(month.getFullYear(), month.getMonth(), 1), lead = (first1.getDay() + 6) % 7;
    const n = new Date(month.getFullYear(), month.getMonth() + 1, 0).getDate(); const cells = [...Array(lead).fill(null)];
    for (let i = 1; i <= n; i++) cells.push(new Date(month.getFullYear(), month.getMonth(), i));
    while (cells.length % 7) cells.push(null); for (let i = 0; i < cells.length; i += 7) weeks.push(cells.slice(i, i + 7));
  }

  return (
    <div className="demo" role="group" aria-label="Booking Demo">
      <div className="demo-banner" role="note"><b>Booking Demo</b><span>All dates, time slots and availability here are illustrative sample data, not real availability. Nothing is sent, saved or booked. Please don’t enter sensitive personal information.</span></div>
      {step < 5 && <><ol className="prog" aria-label="Progress">{LABELS.map((l, i) => <li key={l} className={i < step ? 'done' : i === step ? 'cur' : ''} aria-current={i === step ? 'step' : undefined}><span className="sr">{l}</span></li>)}</ol><p className="prog-t">Step {step + 1} of 5 · {LABELS[step]}</p></>}
      <div className="d-grid">
        <div className="d-main">
          {step === 0 && <div><H n={1}>Choose a service</H>
            <fieldset className="opts"><legend className="sr">Service</legend>
              {SERVICES.map((x) => <label className="opt" key={x.id}><input type="radio" name="svc" checked={s.service === x.id} onChange={() => setS((p) => ({ ...p, service: x.id }))} /><b>{x.name}</b><span>{x.note}</span></label>)}
            </fieldset><p className="note">Example preselected: Guest Henna on Friday 23 October 2026. Change anything you like.</p></div>}

          {step === 1 && <div><H n={2}>Pick a preferred date</H>
            <div className="strip-d" ref={strip} role="group" aria-label="Sample dates, scroll sideways">
              {Array.from({ length: 28 }, (_, i) => new Date(2026, 9, 19 + i)).map((d) => { const st = status(d), k = key(d); return (
                <button key={k} type="button" data-k={k} className={`dchip ${st}`} aria-pressed={s.date === k} aria-disabled={st === 'full'} onClick={() => pickDate(k)}>
                  <small>{DAYS[d.getDay()].slice(0, 3)}</small><strong>{d.getDate()}</strong><small>{MONTHS[d.getMonth()].slice(0, 3)}</small><i>{st === 'full' ? 'full' : st === 'limited' ? 'few' : 'open'}</i><span className="sr">, {long(d)}, {word[st]}</span>
                </button>); })}
            </div>
            <div className="cal">
              <div className="cal-h"><button type="button" aria-label="Previous month" onClick={() => goMonth(-1)} disabled={month <= new Date(2026, 9, 1)}>‹</button><b aria-live="polite">{MONTHS[month.getMonth()]} {month.getFullYear()}</b><button type="button" aria-label="Next month" onClick={() => goMonth(1)} disabled={month >= new Date(2026, 11, 1)}>›</button></div>
              <table className="grid" role="grid" aria-label="Sample calendar" ref={cal} onKeyDown={calKeys}>
                <thead><tr>{['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((d) => <th key={d} scope="col">{d}</th>)}</tr></thead>
                <tbody>{weeks.map((w, i) => <tr key={i}>{w.map((d, j) => { if (!d) return <td key={j} />; const k = key(d), st = status(d), ok = inWin(d), dis = !ok || st === 'full'; return (
                  <td key={j}><button type="button" data-k={k} className={`cd ${ok ? st : 'past'}`} aria-pressed={s.date === k} aria-disabled={dis} tabIndex={k === fd ? 0 : -1} onClick={() => pickDate(k)} aria-label={`${long(d)}, ${ok ? word[st] : 'outside the sample window'}`}>{d.getDate()}</button></td>); })}</tr>)}</tbody>
              </table>
              <ul className="legend" aria-label="Legend"><li><i className="sw-open" />Sample: available</li><li><i className="sw-lim" />Sample: limited</li><li><i className="sw-full" />Sample: unavailable</li><li><i className="sw-sel" />Selected</li></ul>
            </div>
            <p className="note" aria-live="polite">Selected: {long(date)}. Sample window: 19 Oct – 31 Dec 2026.</p>{note && <p className="note" role="status">{note}</p>}</div>}

          {step === 2 && <div><H n={3}>Choose a sample time</H>
            <p className="note" style={{ marginTop: 0 }}>{long(date)} · illustrative slots only</p>
            {['Morning', 'Afternoon', 'Evening'].map((p) => <div key={p}><p className="per">{p}</p><div className="slots">{SLOTS.map(([per, t], i) => per === p && (
              <button key={t} type="button" className="slot" disabled={!slotOpen(date, i)} aria-pressed={s.time === i} onClick={() => { setS((q) => ({ ...q, time: i })); setMsg(''); }}>{t}<small>{slotOpen(date, i) ? 'sample' : 'sample: unavailable'}</small></button>))}</div></div>)}
            <ul className="legend"><li><i />Sample: available</li><li><i className="sw-off" />Sample: unavailable</li><li><i className="sw-sel" />Selected</li></ul></div>}

          {step === 3 && <div><H n={4}>Event details</H>
            <p className="warn">Demonstration only: nothing you type leaves your browser or is stored. Please use made-up details and no sensitive information.</p>
            <div className="f"><label htmlFor="f-name">Name or nickname (demo)<span className="req">required</span></label><input id="f-name" type="text" autoComplete="off" aria-required="true" value={s.form.name} onChange={(e) => setF('name', e.target.value)} {...inv('name')} /><Err id="name" /></div>
            <div className="f"><label htmlFor="f-event">Occasion<span className="req">required</span></label><select id="f-event" aria-required="true" value={s.form.event} onChange={(e) => setF('event', e.target.value)} {...inv('event')}><option value="">Select an occasion</option>{EVENTS.map((x) => <option key={x}>{x}</option>)}</select><Err id="event" /></div>
            <div className="f"><label htmlFor="f-guests">Number of guests<span className="req">required</span></label><div className="stepper"><button type="button" aria-label="Fewer guests" onClick={() => adj(-1)}>−</button><input id="f-guests" type="number" inputMode="numeric" min="1" max="50" aria-required="true" value={s.form.guests} onChange={(e) => setF('guests', e.target.value)} {...inv('guests')} /><button type="button" aria-label="More guests" onClick={() => adj(1)}>+</button></div><Err id="guests" /></div>
            <div className="f"><label htmlFor="f-notes">Notes (optional)</label><textarea id="f-notes" value={s.form.notes} onChange={(e) => setF('notes', e.target.value)} {...inv('notes')} /><p className="hint">{s.form.notes.length}/300 · e.g. style ideas</p><Err id="notes" /></div></div>}

          {step === 4 && <div className="rev"><H n={5}>Review your demo request</H>
            <dl>{[...sum, ['Name (demo)', s.form.name], ['Occasion', s.form.event], ['Guests', s.form.guests], ['Notes', s.form.notes || 'None']].map(([a, b]) => <div key={a}><dt>{a}</dt><dd>{b}</dd></div>)}</dl>
            <div className="bar" style={{ borderTop: 0, marginTop: '.6rem' }}><button className="ed" type="button" onClick={() => setStep(0)}>Edit service/date/time</button><button className="ed" type="button" onClick={() => setStep(3)}>Edit details</button></div>
            <p className="note">Submitting completes the demo only. No request is sent to the artist.</p></div>}

          {step === 5 && <div className="receipt"><h3 ref={head} tabIndex={-1}>Demo request completed</h3>
            <p>This is a website demonstration. No request was sent to the artist, and no appointment has been booked or confirmed.</p>
            <div className="ref">Demo reference: {ref}<span className="sr"> (not a real booking)</span></div>
            <dl style={{ textAlign: 'left', maxWidth: 420, margin: '0 auto 1.4rem', display: 'grid', gap: '.5rem' }}>{[...sum, ['Guests', s.form.guests]].map(([a, b]) => <div key={a}><dt style={{ fontSize: '.75rem', letterSpacing: '.14em', textTransform: 'uppercase', color: 'var(--muted)' }}>{a}</dt><dd style={{ margin: 0 }}>{b}</dd></div>)}</dl>
            <div className="row" style={{ justifyContent: 'center' }}><button className="btn" type="button" onClick={reset}>Start again and clear details</button><a className="btn btn--ghost" href={IG} target="_blank" rel="noopener noreferrer">Message on Instagram <span aria-hidden="true">↗</span><span className="sr"> (opens in a new tab)</span></a></div></div>}

          {msg && step < 5 && <p className="err" role="alert" style={{ marginTop: '1rem' }}>{msg}</p>}
          {step < 5 && <div className="bar"><div className="row">{step > 0 && <button className="btn btn--ghost" type="button" onClick={() => { setMsg(''); setStep(step - 1); }}>Back</button>}{step > 0 && <button className="btn btn--ghost" type="button" onClick={reset}>Start again</button>}</div>
            {step < 4 ? <button className="btn" type="button" onClick={next}>Continue</button> : <button className="btn" type="button" onClick={submit}>Complete demo request</button>}</div>}
        </div>
        {step < 5 && <aside className="d-side" aria-label="Your demo selection"><h4>Your selection</h4>
          <dl>{sum.map(([a, b]) => <div key={a}><dt>{a}</dt><dd className={b ? '' : 'nope'}>{b || 'Not chosen yet'}</dd></div>)}{step >= 3 && s.form.event && <div><dt>Occasion · guests</dt><dd>{s.form.event} · {s.form.guests}</dd></div>}</dl>
          <p className="note">Price: not shown. Sample data only.</p></aside>}
      </div>
    </div>
  );
}
