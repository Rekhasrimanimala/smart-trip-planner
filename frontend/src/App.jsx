import { useState } from 'react'
import { ArrowRight, CalendarDays, CircleAlert, LoaderCircle, MapPin, PlaneTakeoff, Sparkles, Users, Wallet } from 'lucide-react'
import ResultSections from './components/ResultSections.jsx'

const initialForm = {
  origin: '', destination: '', start_date: '', end_date: '', budget: '', currency: 'INR', travelers: '1', preferences: '',
}

export default function App() {
  const [form, setForm] = useState(initialForm)
  const [trip, setTrip] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  function update(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }))
  }

  async function submit(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    setTrip(null)
    try {
      const response = await fetch('/api/plan-trip', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...form, budget: Number(form.budget), travelers: Number(form.travelers) }),
      })
      const payload = await response.json()
      if (!response.ok) {
        const detail = Array.isArray(payload.detail)
          ? payload.detail.map((item) => `${item.loc?.at(-1) || 'Request'}: ${item.msg}`).join(' ')
          : payload.detail || 'Trip planning failed.'
        throw new Error(detail)
      }
      setTrip(payload)
    } catch (issue) {
      setError(issue.message || 'Could not reach the planner. Check that the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="Waypoint home"><span className="brand-mark"><PlaneTakeoff size={18} /></span>waypoint<span className="brand-period">.</span></a>
        <div className="topbar-meta"><span className="live-dot" /> SMART TRIP PLANNER <span className="meta-divider">/</span> BETA</div>
      </header>

      <section className="workspace" id="top">
        <aside className="planning-panel">
          <div className="panel-kicker"><Sparkles size={14} /> YOUR NEXT TRIP, THOUGHT THROUGH</div>
          <h1>Make room<br />for <em>somewhere.</em></h1>
          <p className="intro-copy">A thoughtful route, realistic costs, and the details worth knowing before you go.</p>

          <form onSubmit={submit} className="trip-form">
            <div className="field-pair">
              <label className="field-wrap"><span>DEPARTING FROM</span><span className="input-icon"><PlaneTakeoff size={16} /><input name="origin" value={form.origin} onChange={update} placeholder="e.g. Chennai" required /></span></label>
              <label className="field-wrap"><span>GOING TO</span><span className="input-icon"><MapPin size={16} /><input name="destination" value={form.destination} onChange={update} placeholder="e.g. Singapore" required /></span></label>
            </div>
            <div className="field-pair">
              <label className="field-wrap"><span>ARRIVAL</span><span className="input-icon"><CalendarDays size={16} /><input type="date" name="start_date" value={form.start_date} onChange={update} required /></span></label>
              <label className="field-wrap"><span>RETURN</span><span className="input-icon"><CalendarDays size={16} /><input type="date" name="end_date" value={form.end_date} onChange={update} required /></span></label>
            </div>
            <div className="field-pair budget-row">
              <label className="field-wrap"><span>YOUR BUDGET</span><span className="input-icon"><Wallet size={16} /><input type="number" name="budget" value={form.budget} onChange={update} placeholder="80,000" min="1" step="any" required /></span></label>
              <label className="field-wrap"><span>CURRENCY</span><select name="currency" value={form.currency} onChange={update}><option value="INR">INR · Rupee</option><option value="USD">USD · Dollar</option><option value="EUR">EUR · Euro</option><option value="GBP">GBP · Pound</option><option value="SGD">SGD · Singapore dollar</option><option value="THB">THB · Baht</option></select></label>
            </div>
            <div className="field-pair last-pair">
              <label className="field-wrap"><span>TRAVELLERS</span><span className="input-icon"><Users size={16} /><input type="number" name="travelers" value={form.travelers} onChange={update} min="1" max="20" required /></span></label>
              <label className="field-wrap"><span>PASSPORT COUNTRY</span><input className="plain-input" name="passport_country" value={form.passport_country || 'India'} onChange={update} placeholder="India" /></label>
            </div>
            <label className="field-wrap preferences-field"><span>WHAT DO YOU LIKE?</span><textarea name="preferences" value={form.preferences} onChange={update} placeholder="Food markets, quiet mornings, architecture…" rows="2" /></label>
            <button className="submit-button" type="submit" disabled={loading}>
              {loading ? <><LoaderCircle className="spin" size={18} /> Planning your route</> : <>Plan my trip <ArrowRight size={18} /></>}
            </button>
            <p className="form-note">Dates, budget and departure city are needed to build a costed plan.</p>
          </form>
        </aside>

        <section className="results-panel" aria-live="polite">
          {!trip && !loading && !error && <div className="empty-state">
            <div className="empty-photo" role="img" aria-label="Singapore waterfront at dusk" />
            <div className="empty-caption"><span>START WITH A PLACE</span><strong>Good trips start with a little curiosity.</strong></div>
            <div className="empty-foot"><span>FLIGHTS · STAYS · WEATHER · COSTS</span><span>01 — 04</span></div>
          </div>}
          {loading && <div className="loading-state"><LoaderCircle className="spin" size={28} /><p>Checking routes, weather and the little details.</p><span>This can take a few moments while live sources respond.</span></div>}
          {error && <div className="error-state"><CircleAlert size={22} /><div><strong>We couldn't build that plan.</strong><p>{error}</p></div></div>}
          <ResultSections trip={trip} />
        </section>
      </section>
      <footer className="site-footer"><span>WAYPOINT / SMART TRIP PLANNER</span><span>MOCK FLIGHT + HOTEL DATA · NO BOOKINGS</span></footer>
    </main>
  )
}
