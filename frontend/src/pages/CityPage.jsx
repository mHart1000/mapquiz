import { useParams } from 'react-router-dom'
import { useCallback, useEffect, useRef, useState } from 'react'
import { cities } from '../data/cities'
import CityMap from '../components/CityMap'
import CityInfo from '../components/CityInfo'
import CityQuiz from '../components/CityQuiz'

export default function CityPage() {
  const { city } = useParams()
  const cityData = cities[city]

  const [target, setTarget] = useState(null)
  const [result, setResult] = useState(null)   // { clickedId, correctId, correct }
  const [score, setScore] = useState(0)
  const [attempts, setAttempts] = useState(0)
  const [streak, setStreak] = useState(0)
  const nextTimer = useRef(null)

  const slug = cityData?.slug

  const loadQuestion = useCallback(() => {
    if (!slug) return
    setResult(null)
    fetch(`/api/cities/${slug}/quiz/question/`)
      .then(res => res.json())
      .then(data => setTarget(data.target_name))
      .catch(console.error)
  }, [slug])

  useEffect(() => {
    loadQuestion()
    return () => clearTimeout(nextTimer.current)
  }, [loadQuestion])

  function handleFeatureClick(clickedId) {
    if (result || !target) return   // locked until next question
    fetch(`/api/cities/${slug}/quiz/answer/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_name: target, clicked_id: clickedId }),
    })
      .then(res => res.json())
      .then(data => {
        setResult({ clickedId, correctId: data.correct_id, correct: data.correct })
        setAttempts(a => a + 1)
        setScore(s => s + (data.correct ? 1 : 0))
        setStreak(st => (data.correct ? st + 1 : 0))
        nextTimer.current = setTimeout(loadQuestion, 1500)
      })
      .catch(console.error)
  }

  function handleReset() {
    clearTimeout(nextTimer.current)
    setScore(0)
    setAttempts(0)
    setStreak(0)
    loadQuestion()
  }

  if (!cityData) return <p>City not found</p>

  return (
    <div className="city-page">
      <CityInfo city={cityData} />
      <CityQuiz
        target={target}
        score={score}
        attempts={attempts}
        streak={streak}
        result={result}
        onReset={handleReset}
      />
      <CityMap city={cityData} onFeatureClick={handleFeatureClick} result={result} />
    </div>
  )
}
