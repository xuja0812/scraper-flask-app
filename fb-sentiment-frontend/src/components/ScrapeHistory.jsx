import React, { useEffect, useState } from 'react'
import {
  LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer,
} from 'recharts'
import './ScrapeHistory.css'

function ScrapeHistory() {
  const [scrapes, setScrapes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [urlInput, setUrlInput] = useState('')
  const [filteredScrapes, setFilteredScrapes] = useState([])

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

  function handleSubmit(e) {
    e.preventDefault()
    if (!urlInput.trim()) {
      setFilteredScrapes([])
      return
    }
    const filtered = scrapes
      .filter(s => s.url.toLowerCase() === urlInput.trim().toLowerCase())
      .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
    setFilteredScrapes(filtered)
  }

  const chartData = filteredScrapes.map(scrape => ({
    date: new Date(scrape.created_at).toLocaleDateString(),
    average_score: scrape.average_score !== null ? scrape.average_score : 0,
  }))

  if (loading) return <p>Loading past scrapes...</p>
  if (error) return <p className="scrape-history-error">Error: {error}</p>
  if (scrapes.length === 0) return <p>No past scrapes found.</p>

  return (
    <div className="scrape-history-container">
      <h2 className="scrape-history-title">Your Past Scrapes</h2>

      <form onSubmit={handleSubmit} className="scrape-history-form">
        <label htmlFor="urlInput">Enter URL to analyze:</label>
        <input
          id="urlInput"
          type="text"
          value={urlInput}
          onChange={e => setUrlInput(e.target.value)}
          placeholder="https://example.com"
          className="scrape-history-input"
        />
        <button type="submit" className="scrape-history-button">Submit</button>
      </form>

      {filteredScrapes.length > 0 ? (
        <div className="scrape-history-graph">
          <h3>Sentiment Over Time for {urlInput}</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={[-1, 1]} />
              <Tooltip />
              <Line type="monotone" dataKey="average_score" stroke="#8884d8" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : urlInput.trim() !== '' ? (
        <p>No scrapes found for this URL.</p>
      ) : null}

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
