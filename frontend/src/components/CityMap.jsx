import { useEffect, useState } from 'react'
import { MapContainer, GeoJSON, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Recenter/zoom the map to the loaded neighborhood layer.
function FitBounds({ data }) {
  const map = useMap()
  useEffect(() => {
    if (!data) return
    const bounds = L.geoJSON(data).getBounds()
    if (bounds.isValid()) map.fitBounds(bounds, { padding: [20, 20] })
  }, [data, map])
  return null
}

const baseStyle = { color: '#555', weight: 1, fillColor: '#cbd5e0', fillOpacity: 0.4 }
const hoverStyle = { color: '#2b6cb0', weight: 2, fillColor: '#90cdf4', fillOpacity: 0.6 }
const correctStyle = { color: '#22543d', weight: 2, fillColor: '#48bb78', fillOpacity: 0.7 }
const wrongStyle = { color: '#742a2a', weight: 2, fillColor: '#f56565', fillOpacity: 0.7 }

export default function CityMap({ city, onFeatureClick, result }) {
  const [geoData, setGeoData] = useState(null)

  useEffect(() => {
    fetch(`/api/cities/${city.slug}/neighborhoods/`)
      .then(res => res.json())
      .then(setGeoData)
      .catch(console.error)
  }, [city.slug])

  function styleFor(feature) {
    if (result) {
      if (feature.id === result.correctId) return correctStyle
      if (feature.id === result.clickedId && !result.correct) return wrongStyle
    }
    return baseStyle
  }

  function onEachFeature(feature, layer) {
    layer.on({
      click: () => onFeatureClick(feature.id),
      mouseover: () => { if (!result) layer.setStyle(hoverStyle) },
      mouseout: () => { if (!result) layer.setStyle(baseStyle) },
    })
  }

  return (
    <MapContainer
      style={{ height: '500px', width: '100%', background: '#f7fafc' }}
      center={[32.7157, -117.1611]}
      zoom={10}
    >
      {geoData && (
        <>
          {/* key forces a restyle/remount when the answer result changes */}
          <GeoJSON
            key={result ? `${result.clickedId}-${result.correctId}` : 'idle'}
            data={geoData}
            style={styleFor}
            onEachFeature={onEachFeature}
          />
          <FitBounds data={geoData} />
        </>
      )}
    </MapContainer>
  )
}
