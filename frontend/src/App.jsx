import { useEffect, useState } from 'react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_URL || '/api'

function App() {
  const [documents, setDocuments] = useState([])
  const [metrics, setMetrics] = useState(null)
  const [name, setName] = useState('')
  const [content, setContent] = useState('')
  const [selected, setSelected] = useState(null)
  const [checkpoints, setCheckpoints] = useState([])
  const [busy, setBusy] = useState(false)

  const fetchDocuments = async () => {
    const res = await fetch(`${API_BASE}/documents/`)
    const data = await res.json()
    setDocuments(data)
  }

  const fetchMetrics = async () => {
    const res = await fetch(`${API_BASE}/metrics/`)
    const data = await res.json()
    setMetrics(data)
  }

  useEffect(() => {
    fetchDocuments()
    fetchMetrics()
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setBusy(true)
    await fetch(`${API_BASE}/documents/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, content }),
    })
    setName('')
    setContent('')
    await fetchDocuments()
    await fetchMetrics()
    setBusy(false)
  }

  const handleReplay = async (id) => {
    setBusy(true)
    await fetch(`${API_BASE}/replay/${id}`, { method: 'POST' })
    await fetchDocuments()
    await fetchMetrics()
    if (selected?.id === id) {
      await loadCheckpoints(id)
    }
    setBusy(false)
  }

  const loadCheckpoints = async (id) => {
    const res = await fetch(`${API_BASE}/checkpoint/${id}`)
    const data = await res.json()
    setCheckpoints(data)
  }

  const selectDocument = async (doc) => {
    setSelected(doc)
    await loadCheckpoints(doc.id)
  }

  const stageBadge = (stage) => {
    const map = {
      completed: 'badge-green',
      failed: 'badge-red',
      dead_letter: 'badge-black',
      pending: 'badge-gray',
    }
    return map[stage] || 'badge-blue'
  }

  return (
    <div className="container">
      <header>
        <h1>RAG Ingestion Checkpoint Workbench</h1>
        <p>수집 → 청크 → 임베딩 → 색인까지 checkpoint/replay 기반 RAG 파이프라인</p>
      </header>

      <section className="card">
        <h2>새 문서 수집</h2>
        <form onSubmit={handleSubmit}>
          <input
            placeholder="파일 이름"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <textarea
            placeholder="문서 본문"
            rows={6}
            value={content}
            onChange={(e) => setContent(e.target.value)}
            required
          />
          <button type="submit" disabled={busy}>
            {busy ? '처리 중...' : '수집 실행'}
          </button>
        </form>
      </section>

      {metrics && (
        <section className="card metrics">
          <h2>파이프라인 상태</h2>
          <div className="metric-grid">
            <div className="metric"><strong>전체 문서</strong><span>{metrics.total}</span></div>
            <div className="metric"><strong>Dead Letter</strong><span>{metrics.dead_letter_count}</span></div>
            <div className="metric"><strong>평균 청크</strong><span>{metrics.average_chunks.toFixed(1)}</span></div>
            <div className="metric"><strong>평균 벡터</strong><span>{metrics.average_vectors.toFixed(1)}</span></div>
          </div>
          <ul className="stage-list">
            {Object.entries(metrics.by_stage).map(([stage, count]) => (
              <li key={stage}><span className={`badge ${stageBadge(stage)}`}>{stage}</span> {count}</li>
            ))}
          </ul>
        </section>
      )}

      <section className="card">
        <h2>문서 목록</h2>
        <table>
          <thead>
            <tr><th>ID</th><th>이름</th><th>단계</th><th>청크</th><th>벡터</th><th>동작</th></tr>
          </thead>
          <tbody>
            {documents.map((doc) => (
              <tr key={doc.id}>
                <td>{doc.id}</td>
                <td>{doc.name}</td>
                <td><span className={`badge ${stageBadge(doc.stage)}`}>{doc.stage}</span></td>
                <td>{doc.chunks_count}</td>
                <td>{doc.vectors_count}</td>
                <td>
                  <button onClick={() => selectDocument(doc)}>상세</button>
                  {doc.stage !== 'completed' && (
                    <button onClick={() => handleReplay(doc.id)} disabled={busy}>재실행</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      {selected && (
        <section className="card">
          <h2>문서 #{selected.id} 체크포인트</h2>
          <ol className="checkpoint-list">
            {checkpoints.map((cp) => (
              <li key={cp.id}>
                <span className={`badge ${stageBadge(cp.stage)}`}>{cp.stage}</span>
                <small>{new Date(cp.created_at).toLocaleString()}</small>
                {cp.payload && <code>{cp.payload}</code>}
              </li>
            ))}
          </ol>
        </section>
      )}
    </div>
  )
}

export default App
