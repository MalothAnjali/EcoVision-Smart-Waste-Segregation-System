import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Classify from './pages/Classify'
import LiveDetection from './pages/LiveDetection'
import PastDetections from './pages/PastDetections'
import Chatbot from './pages/Chatbot'
import Layout from './components/Layout'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    // Check if user is logged in
    const loggedIn = localStorage.getItem('ecovision_auth') === 'true'
    setIsAuthenticated(loggedIn)
  }, [])

  const handleLogin = () => {
    localStorage.setItem('ecovision_auth', 'true')
    setIsAuthenticated(true)
  }

  const handleLogout = () => {
    localStorage.removeItem('ecovision_auth')
    setIsAuthenticated(false)
  }

  return (
    <Router>
      <Routes>
        <Route 
          path="/login" 
          element={
            isAuthenticated ? 
            <Navigate to="/dashboard" /> : 
            <Login onLogin={handleLogin} />
          } 
        />
        
        <Route
          path="/*"
          element={
            isAuthenticated ? (
              <Layout onLogout={handleLogout}>
                <Routes>
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/classify" element={<Classify />} />
                  <Route path="/live-detection" element={<LiveDetection />} />
                  <Route path="/chatbot" element={<Chatbot />} />
                  <Route path="/history" element={<PastDetections />} />
                  <Route path="/" element={<Navigate to="/dashboard" />} />
                </Routes>
              </Layout>
            ) : (
              <Navigate to="/login" />
            )
          }
        />
      </Routes>
    </Router>
  )
}

export default App