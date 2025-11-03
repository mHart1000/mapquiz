import { useEffect, useState } from 'react'
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet'

export default function CityMap({ city }) {
  const [geoData, setGeoData] = useState(null)

  useEffect(() => {
    fetch(`http://192.168.0.241:8000/api/cities/${city.slug}/`)
      .then(res => res.json())
      .then(setGeoData)
      .catch(console.error)
  }, [city.slug])

  return (
    <MapContainer style={{ height: '500px', width: '100%' }} center={[32.7157, -117.1611]} zoom={10}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {geoData && <GeoJSON data={geoData} />}
    </MapContainer>
  )
}
