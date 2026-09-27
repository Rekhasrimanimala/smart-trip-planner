import { CalendarDays, CloudSun, Compass, Hotel, Plane, ShieldAlert, Ticket, Wallet } from 'lucide-react'

const money = (value, currency) => new Intl.NumberFormat(undefined, {
  style: 'currency', currency, maximumFractionDigits: 0,
}).format(value || 0)

function Section({ icon: Icon, title, children, className = '' }) {
  return (
    <section className={`result-section ${className}`}>
      <div className="section-heading"><Icon size={18} strokeWidth={1.8} /><h2>{title}</h2></div>
      {children}
    </section>
  )
}

function Lines({ items, empty = 'No information returned.' }) {
  if (!items?.length) return <p className="muted">{empty}</p>
  return <ul className="line-list">{items.map((item, index) => <li key={`${index}-${item}`}>{item}</li>)}</ul>
}

export default function ResultSections({ trip }) {
  if (!trip) return null
  const summary = trip.trip_summary
  const costs = trip.budget_breakdown
  return (
    <div className="results">
      <div className="results-topline">
        <div>
          <span className="eyebrow">YOUR ROUTE, AT A GLANCE</span>
          <h2>{summary.origin} <span className="route-arrow">→</span> {summary.destination}</h2>
          <p>{summary.start_date} to {summary.end_date} · {summary.travelers} traveller{summary.travelers === 1 ? '' : 's'}</p>
        </div>
        <div className={`budget-status ${costs.budget_met ? 'within' : 'over'}`}>
          <span>{costs.budget_met ? 'Within budget' : 'Over budget'}</span>
          <strong>{money(costs.total, costs.currency)}</strong>
        </div>
      </div>

      <div className="results-grid">
        <Section icon={Plane} title="Flight options">
          {!trip.flights?.length ? <p className="muted">No mock flights found for this route.</p> : trip.flights.map((flight) => (
            <div className="option-row" key={flight.flight_number}>
              <div><strong>{flight.airline}</strong><span>{flight.flight_number} · {flight.departure}–{flight.arrival}</span></div>
              <b>{money(flight.price, flight.currency)}</b>
            </div>
          ))}
          <p className="micro-note">Mock one-way fares; budget estimate assumes a return journey.</p>
        </Section>

        <Section icon={Hotel} title="Hotel options">
          {!trip.hotels?.length ? <p className="muted">No mock hotels found for this destination.</p> : trip.hotels.map((hotel) => (
            <div className="option-row" key={hotel.name}>
              <div><strong>{hotel.name}</strong><span>{hotel.rating} / 5 · per night</span></div>
              <b>{money(hotel.price_per_night, hotel.currency)}</b>
            </div>
          ))}
        </Section>

        <Section icon={CloudSun} title="Weather" className="wide-section">
          <div className="weather-strip">
            {trip.weather?.days?.length ? trip.weather.days.map((day) => (
              <div className="weather-day" key={day.date}>
                <span>{new Date(`${day.date}T12:00:00`).toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' })}</span>
                <strong>{day.temperature_min_c}° <i>·</i> {day.temperature_max_c}°</strong>
                <small>{day.precipitation_probability ?? '—'}% rain chance</small>
              </div>
            )) : <p className="muted">{trip.weather?.note || trip.weather?.error || 'Forecast unavailable for these dates.'}</p>}
          </div>
          {trip.weather?.note && <p className="micro-note">{trip.weather.note}</p>}
        </Section>

        <Section icon={CalendarDays} title="Day-by-day itinerary" className="wide-section itinerary-section">
          <div className="day-list">
            {trip.itinerary?.map((day, index) => (
              <article className="day-row" key={day.date}>
                <div className="day-date"><span>DAY {String(index + 1).padStart(2, '0')}</span><strong>{day.date}</strong></div>
                <div className="day-slots">
                  <div><small>MORNING</small><p>{day.morning}</p></div>
                  <div><small>AFTERNOON</small><p>{day.afternoon}</p></div>
                  <div><small>EVENING</small><p>{day.evening}</p></div>
                </div>
              </article>
            ))}
          </div>
        </Section>

        <Section icon={Wallet} title="Estimated budget">
          <dl className="cost-list">
            {[['Flights', costs.flights], ['Hotels', costs.hotels], ['Food', costs.food], ['Transport', costs.transport], ['Activities', costs.activities]].map(([label, value]) => (
              <div key={label}><dt>{label}</dt><dd>{money(value, costs.currency)}</dd></div>
            ))}
            <div className="cost-total"><dt>Total estimate</dt><dd>{money(costs.total, costs.currency)}</dd></div>
            <div><dt>Your budget</dt><dd>{money(costs.budget, costs.currency)}</dd></div>
            <div><dt>Remaining</dt><dd>{money(costs.remaining, costs.currency)}</dd></div>
          </dl>
          <p className="micro-note">{trip.planning_attempts ? `Re-planned ${trip.planning_attempts} time${trip.planning_attempts === 1 ? '' : 's'} to reduce cost.` : 'Includes mock return airfare and estimated daily expenses.'}</p>
        </Section>

        <Section icon={ShieldAlert} title="Visa & entry">
          <p className="body-copy">{trip.visa?.information}</p>
          <p className="source-label">KNOWLEDGE SOURCES</p>
          <Lines items={trip.visa?.sources} empty="No source could be retrieved." />
          <p className="warning-copy">Visa requirements can change. Please verify the latest requirements with the relevant official embassy or immigration website before travelling.</p>
        </Section>

        <Section icon={Ticket} title="Events & festivals">
          <Lines items={[...(trip.events || []), ...(trip.festivals || [])]} empty="No current search results available." />
        </Section>

        <Section icon={Compass} title="Closures & advisories">
          <Lines items={[...(trip.closures || []), ...(trip.advisories || [])]} empty="No current search results available." />
        </Section>
      </div>

      <div className="result-warnings">
        {trip.warnings?.map((warning, index) => <p key={`${index}-${warning}`}>{warning}</p>)}
        <p>Flight and hotel prices are indicative and may change. Please verify prices before booking.</p>
      </div>
    </div>
  )
}
