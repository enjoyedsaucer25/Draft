import React, { useEffect, useState } from 'react'

type Player = {
  player_id: string
  clean_name: string
  position: string
  team: string
  tier?: number
  ecr_rank?: number
  blended_rank?: number
  adp?: number
}

type Suggestion = { top: Player[]; next: Player[] }

const App: React.FC = () => {
  const [players, setPlayers] = useState<Player[]>([])
  const [sugs, setSugs] = useState<Suggestion | null>(null)
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState<string>('')

  async function refresh() {
    setLoading(true)
    try {
      const r = await fetch('/api/refresh', { method: 'POST' })
      const jr = await r.json()
      setMsg('Data refreshed. Now loading players...')
      const p = await fetch('/api/players')
      setPlayers(await p.json())
      const s = await fetch('/api/suggestions')
      setSugs(await s.json())
      setMsg('Ready.')
    } catch (e) {
      setMsg('Refresh failed: ' + (e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    (async () => {
      const st = await fetch('/api/status')
      if (st.ok) {
        await refresh()
      }
    })()
  }, [])

  return (
    <div style={{fontFamily:'Inter, system-ui, Arial', padding:16, background:'#0b0e13', color:'#e6e6e6', minHeight:'100vh'}}>
      <header style={{display:'flex', alignItems:'center', gap:12}}>
        <h1 style={{margin:0}}>Draft Assistant</h1>
        <button disabled={loading} onClick={refresh}>Refresh</button>
        <span>{msg}</span>
      </header>

      <section style={{display:'grid', gridTemplateColumns:'1fr 2fr 1fr', gap:16, marginTop:16}}>
        <div>
          <h3>Your Roster</h3>
          <div style={{opacity:.7}}>Coming soon: live roster tiles & needs</div>
          <h3 style={{marginTop:24}}>On Deck</h3>
          {sugs && (
            <div>
              {sugs.top.map(p => (
                <div key={p.player_id} style={{padding:8, border:'1px solid #333', borderRadius:8, marginBottom:8}}>
                  <div style={{fontWeight:700}}>{p.clean_name} <span style={{opacity:.6}}>{p.position}-{p.team}</span></div>
                  <div style={{fontSize:12, opacity:.8}}>Tier {p.tier ?? '-'} · ECR {p.ecr_rank ?? '-'} · ADP {p.adp ?? '-'}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div>
          <h3>Players</h3>
          <div style={{maxHeight: '70vh', overflow:'auto', border:'1px solid #222', borderRadius:8}}>
            <table style={{width:'100%', borderCollapse:'collapse'}}>
              <thead>
                <tr style={{background:'#111'}}>
                  <th style={{textAlign:'left', padding:8}}>Name</th>
                  <th>Pos</th>
                  <th>Team</th>
                  <th>Tier</th>
                  <th>ECR</th>
                  <th>ADP</th>
                  <th>Blend</th>
                </tr>
              </thead>
              <tbody>
                {players.map(p => (
                  <tr key={p.player_id} style={{borderTop:'1px solid #222'}}>
                    <td style={{padding:8}}>{p.clean_name}</td>
                    <td style={{textAlign:'center'}}>{p.position}</td>
                    <td style={{textAlign:'center'}}>{p.team}</td>
                    <td style={{textAlign:'center'}}>{p.tier ?? ''}</td>
                    <td style={{textAlign:'center'}}>{p.ecr_rank ?? ''}</td>
                    <td style={{textAlign:'center'}}>{p.adp ?? ''}</td>
                    <td style={{textAlign:'center'}}>{p.blended_rank?.toFixed(1) ?? ''}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div>
          <h3>Next Up</h3>
          {sugs && sugs.next.map(p => (
            <div key={p.player_id} style={{padding:8, border:'1px dashed #333', borderRadius:8, marginBottom:8}}>
              <div style={{fontWeight:600}}>{p.clean_name} <span style={{opacity:.6}}>{p.position}-{p.team}</span></div>
              <div style={{fontSize:12, opacity:.8}}>Tier {p.tier ?? '-'} · ECR {p.ecr_rank ?? '-'} · ADP {p.adp ?? '-'}</div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}

export default App
