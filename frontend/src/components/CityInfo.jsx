export default function CityInfo({ city }) {
  return (
    <div>
      <h1>{city.name}</h1>
      <p>{city.description}</p>
    </div>
  )
}
