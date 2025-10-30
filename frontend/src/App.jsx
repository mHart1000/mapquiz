import { Routes, Route, Link } from 'react-router-dom'
import HomePage from './pages/HomePage'
import SanDiegoPage from './pages/SanDiegoPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/san-diego" element={<SanDiegoPage />} />
    </Routes>
  )
}

export default App
