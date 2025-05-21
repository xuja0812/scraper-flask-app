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
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={300}>
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
          <Legend verticalAlign="bottom" height={36} />
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
  const [commonWords, setCommonWords] = useState([])
  const [commonComplaints, setCommonComplaints] = useState([])
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
      setCommonWords([])
      setCommonComplaints([])
      return
    }

    setLoading(true)
    setResult('')
    setSummary(null)
    setCommonWords([])
    setCommonComplaints([])

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
        setCommonWords([])
        setCommonComplaints([])
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
        setCommonWords(data.common_words || [])
        setCommonComplaints(data.common_complaints || [])
      } else {
        setResult('No data returned')
        setSummary(null)
        setCommonWords([])
        setCommonComplaints([])
      }
    } catch (err) {
      setResult('Error fetching results. Check if the backend is running.')
      setSummary(null)
      setCommonWords([])
      setCommonComplaints([])
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
    setCommonWords([])
    setCommonComplaints([])
  }

  return (
    <div className="app-container">
      <h1>Google Review Sentiment Analyzer</h1>

      {loggedInUser ? (
        <div className="auth-welcome">
          <p>Welcome, <strong>{loggedInUser}</strong>!</p>
          <button onClick={handleLogout} className="btn-logout">Logout</button>
        </div>
      ) : (
        <div className="auth-welcome">
          <h3>Login or Register</h3>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="input-auth"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="input-auth"
          />
          <div className="auth-buttons">
            <button onClick={handleLogin} className="btn-primary">Login</button>
            <button onClick={handleRegister} className="btn-secondary">Register</button>
          </div>
          {authError && <p className="auth-error">{authError}</p>}
        </div>
      )}

      <form onSubmit={handleSubmit} className="form-container">
        <label>
          Google Business URL:
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            required
            placeholder="https://www.google.com/maps/place/BusinessName/"
            className="input-form"
          />
        </label>

        <label>
          Number of Reviews:
          <input
            type="number"
            value={numReviews}
            onChange={(e) => setNumReviews(Number(e.target.value))}
            min="1"
            max="100"
            required
            className="input-form"
          />
        </label>

        <button type="submit" disabled={loading || !loggedInUser} className="btn-primary">
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>
      </form>

      <pre className="result-box">{result}</pre>

      {summary && (
        <div className="summary-section">
          <h2>Sentiment Summary</h2>
          <SentimentChart summary={summary} />

          {commonWords.length > 0 && (
            <div className="common-words">
              <h3>Most Common Words</h3>
              <ul>
                {commonWords.map(({ phrase, count }, index) => (
                  <li key={index}>{phrase} ({count})</li>
                ))}
              </ul>
            </div>
          )}

          {commonComplaints.length > 0 ? (
            <div className="common-complaints">
              <h3>Complaints</h3>
              <ul className="list-disc list-inside">
                {commonComplaints.map((snippet, index) => (
                  <li key={index} className="text-sm text-gray-800">
                    {snippet}
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <p className="text-gray-500 italic">No complaints found.</p>
          )}
        </div>
      )}

      {loggedInUser && (
        <div className="history-section">
          <ScrapeHistory />
        </div>
      )}
    </div>
  )
}

export default App
