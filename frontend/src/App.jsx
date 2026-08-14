import { useState, useEffect } from 'react'
import './App.css'
import api from './services/api'

function App() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const response = await api.get('/health')
      setData(response.data)
      setError(null)
    } catch (err) {
      setError(err.message)
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to DataBound AI</h1>
        <p>Full-Stack Application</p>
      </header>
      
      <main className="App-main">
        {loading && <p>Loading...</p>}
        {error && <p className="error">Error: {error}</p>}
        {data && (
          <div className="status">
            <h2>Server Status</h2>
            <p><strong>Status:</strong> {data.status}</p>
            <p><strong>Message:</strong> {data.message}</p>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
