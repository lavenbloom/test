import React from 'react'

// Env var injection helper
const apiUrl = (window as any).__env__?.REACT_APP_API_URL || import.meta.env.VITE_API_URL || 'http://localhost:8080';

function App() {
  return (
    <div style={{ fontFamily: 'Inter, sans-serif', padding: '2rem', background: '#1a1a1a', color: '#fff', minHeight: '100vh' }}>
      <h1>Habit Intelligence Platform</h1>
      <p>API Gateway URL: {apiUrl}</p>
      <div style={{ marginTop: '2rem' }}>
        <p>Frontend scaffolding complete.</p>
        <p>The habit grid, metrics charts, and journal features will be built out here.</p>
      </div>
    </div>
  )
}

export default App
