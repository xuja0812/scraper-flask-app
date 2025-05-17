import React, { useState, useEffect } from 'react'
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import ScrapeHistory from './components/ScrapeHistory'
import './App.css'

const COLORS = ['#4CAF50', '#FFC107', '#F44336']

function SentimentChart({ summary }) {
  if (!summary) return null
  const data = [
    { name: 'Positive', value: summary.positive },
    { name: 'Negative', value: summary.negative },
    { name: 'Neutral', value: summary.total - summary.positive - summary.negative },
  ]

  return (
    <div style={{ width: '100%', height: 300 }}>
      <ResponsiveContainer>
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            outerRadius={100}
            label
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}

function App() {
  const [url, setUrl] = useState('')
  const [numReviews, setNumReviews] = useState(10)
  const [result, setResult] = useState('')
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loggedInUser, setLoggedInUser] = useState(null)
  const [authError, setAuthError] = useState('')

  useEffect(() => {
    fetch('/api/login', { credentials: 'include' }).then(res => {
      if (res.ok) {
        res.json().then(data => setLoggedInUser(data.username))
      }
    })
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!loggedInUser) {
      setResult('Please log in to analyze reviews.')
      setSummary(null)
      return
    }

    setLoading(true)
    setResult('')
    setSummary(null)

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ url, num_reviews: numReviews }),
      })

      const data = await response.json()

      if (data.error) {
        setResult(`Error: ${data.error}`)
        setSummary(null)
      } else if (data.summary) {
        const { total, positive, negative, average_score } = data.summary
        const positiveSample = data.positive_reviews?.[0]?.text || 'None'
        const negativeSample = data.negative_reviews?.[0]?.text || 'None'

        const formatted =
          `Total Reviews: ${total}\n` +
          `Positive Reviews: ${positive}\n` +
          `Negative Reviews: ${negative}\n` +
          `Average Sentiment Score: ${average_score.toFixed(2)}\n\n` +
          `Sample Positive Review:\n${positiveSample}\n\n` +
          `Sample Negative Review:\n${negativeSample}`

        setResult(formatted)
        setSummary(data.summary)
      } else {
        setResult('No data returned')
        setSummary(null)
      }
    } catch (err) {
      setResult('Error fetching results. Check if the backend is running.')
      setSummary(null)
    } finally {
      setLoading(false)
    }
  }

  const handleLogin = async () => {
    setAuthError('')
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ username, password }),
    })
    const data = await response.json()
    if (response.ok) {
      setLoggedInUser(data.username)
      setUsername('')
      setPassword('')
    } else {
      setAuthError(data.error || 'Login failed')
    }
  }

  const handleRegister = async () => {
    setAuthError('')
    const response = await fetch('/api/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ username, password }),
    })
    const data = await response.json()
    if (response.ok) {
      await handleLogin()
    } else {
      setAuthError(data.error || 'Registration failed')
    }
  }

  const handleLogout = async () => {
    await fetch('/api/logout', { method: 'POST', credentials: 'include' })
    setLoggedInUser(null)
    setResult('')
    setSummary(null)
  }

  return (
    <div className="app-container">
      <h1>Google Review Sentiment Analyzer</h1>

      {loggedInUser ? (
        <div className="welcome-section">
          <p>Welcome, {loggedInUser}!</p>
          <button onClick={handleLogout}>Logout</button>
        </div>
      ) : (
        <div className="auth-section">
          <h3>Login or Register</h3>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="auth-input"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="auth-input"
          />
          <div style={{ display: 'flex', flexWrap: 'wrap' }}>
            <button onClick={handleLogin} style={{ marginRight: '1rem', marginBottom: '0.5rem' }}>
              Login
            </button>
            <button onClick={handleRegister} style={{ marginBottom: '0.5rem' }}>
              Register
            </button>
          </div>
          {authError && <p className="auth-error">{authError}</p>}
        </div>
      )}

      <form onSubmit={handleSubmit} className="form">
        <label>
          Google Business URL:
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            required
            placeholder="https://www.google.com/maps/place/BusinessName/"
            className="form-input"
          />
        </label>

        <label>
          Number of Reviews:
          <input
            type="number"
            value={numReviews}
            onChange={(e) => setNumReviews(Number(e.target.value))}
            min="1"
            max="20"
            required
            className="form-input"
          />
        </label>

        <button type="submit" disabled={loading || !loggedInUser}>
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>
      </form>

      <pre className="result">{result}</pre>

      {summary && (
        <div className="chart-section">
          <h2>Sentiment Summary</h2>
          <SentimentChart summary={summary} />
        </div>
      )}

      {loggedInUser && (
        <div className="scrape-history-section">
          <ScrapeHistory />
        </div>
      )}
    </div>
  )
}

export default App
