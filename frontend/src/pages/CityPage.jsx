import { useParams } from 'react-router-dom'
import { cities } from '../data/cities'
import CityMap from '../components/CityMap'
import CityInfo from '../components/CityInfo'
import CityQuiz from '../components/CityQuiz'

export default function CityPage() {
  const { city } = useParams()
  const cityData = cities[city]

  if (!cityData) return <p>City not found</p>

  return (
    <div className="city-page">
      <CityInfo city={cityData} />
      <CityMap city={cityData} />
      <CityQuiz city={cityData} />
    </div>
  )
}
