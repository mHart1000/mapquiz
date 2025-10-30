import { Link } from 'react-router-dom'

function HomePage() {
  return (
    <div style={{ textAlign: 'center', marginTop: '3rem' }}>
      <h1>Welcome to the Map Quiz App</h1>
      <p>Select a city to start</p>
      <Link to="/san-diego">Go to San Diego</Link>
    </div>
  )
}

export default HomePage
