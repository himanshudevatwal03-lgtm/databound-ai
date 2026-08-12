import React, { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [backendStatus, setBackendStatus] = useState('loading')
  const [error, setError] = useState(null)

  useEffect(() => {
    // Check backend health on mount
    fetch('/api/health')
      .then((res) => res.json())
      .then((data) => {
        if (data.status === 'ok') {
          setBackendStatus('connected')
        }
      })
      .catch((err) => {
        setError('Failed to connect to backend')
        setBackendStatus('disconnected')
      })
  }, [])

  return (
    <div className="container">
      <header className="header">
        <h1>🚀 DataBound AI</h1>
        <p>Data-grounded question-answering platform</p>
      </header>

      <main className="main">
        <div className="status-card">
          <h2>Status</h2>
          <div className={`status-indicator ${backendStatus}`}>
            <span className="dot"></span>
            <span>Backend: {backendStatus}</span>
          </div>

          {error && <div className="error-message">{error}</div>}

          {backendStatus === 'connected' && (
            <div className="welcome-message">
              <p>✅ Backend is running!</p>
              <p>Frontend and backend are connected.</p>
            </div>
          )}
        </div>

        <div className="features-card">
          <h2>Phase 1 - Foundation</h2>
          <ul>
            <li>✅ Project structure</li>
            <li>✅ FastAPI backend</li>
            <li>✅ React frontend</li>
            <li>✅ PostgreSQL + pgvector</li>
            <li>✅ Docker setup</li>
            <li>✅ Health checks</li>
          </ul>
        </div>

        <div className="info-card">
          <h2>🔗 Quick Links</h2>
          <ul>
            <li>
              <a href="/api/docs" target="_blank" rel="noopener noreferrer">
                API Documentation (Swagger)
              </a>
            </li>
            <li>
              <a href="/api/redoc" target="_blank" rel="noopener noreferrer">
                API Documentation (ReDoc)
              </a>
            </li>
            <li>
              <a
                href="https://github.com/himanshudevatwal03-lgtm/databound-ai"
                target="_blank"
                rel="noopener noreferrer"
              >
                GitHub Repository
              </a>
            </li>
          </ul>
        </div>

        <div className="next-steps">
          <h2>📋 Next Steps</h2>
          <p>Phase 2: Authentication (registration, login, JWT)</p>
        </div>
      </main>

      <footer className="footer">
        <p>DataBound AI © 2024 | A GitHub Portfolio Project</p>
      </footer>
    </div>
  )
}

export default App
