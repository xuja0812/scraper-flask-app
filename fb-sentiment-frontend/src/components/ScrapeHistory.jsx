import React, { useEffect, useState } from 'react'
import './ScrapeHistory.css'

function ScrapeHistory() {
  const [scrapes, setScrapes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function fetchScrapes() {
      try {
        const res = await fetch('/api/scrapes', { credentials: 'include' })
        if (!res.ok) {
          throw new Error('Failed to fetch scrapes')
        }
        const data = await res.json()
        setScrapes(data.scrapes)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    fetchScrapes()
  }, [])

  if (loading) return <p>Loading past scrapes...</p>
  if (error) return <p className="scrape-history-error">Error: {error}</p>
  if (scrapes.length === 0) return <p>No past scrapes found.</p>

  return (
    <div className="scrape-history-container">
      <h2 className="scrape-history-title">Your Past Scrapes</h2>
      <div className="scrape-history-scroll">
        <table className="scrape-history-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>URL</th>
              <th>Positive</th>
              <th>Negative</th>
              <th>Neutral</th>
              <th>Total</th>
              <th>Avg. Score</th>
            </tr>
          </thead>
          <tbody>
            {scrapes.map((scrape) => (
              <tr key={scrape.id}>
                <td>{new Date(scrape.created_at).toLocaleString()}</td>
                <td>
                  <a href={scrape.url} target="_blank" rel="noopener noreferrer">
                    {scrape.url}
                  </a>
                </td>
                <td>{scrape.positive}</td>
                <td>{scrape.negative}</td>
                <td>{scrape.neutral}</td>
                <td>{scrape.total}</td>
                <td>{scrape.average_score !== null ? scrape.average_score.toFixed(2) : '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default ScrapeHistory
