import React, { useEffect, useState } from 'react'

function HomeView({ onNavigate }) {
  return (
    <div className="home">
      <header className="brand-hero">
        <h1>Sovereign Verily</h1>
        <p>Flagship agentic swarm intelligence system — a coming-soon fusion of ancient architecture and modern AI lattice.</p>
        <button className="cta" onClick={() => onNavigate('#atlantiplex')}>Enter Atlantiplex Studio</button>
      </header>
      <section className="tiles">
        <div className="tile">
          <h3>The Sovereign Node Architecture</h3>
          <p>Self-assembling node fabric • watcher-lattice • swarm cognition</p>
        </div>
        <div className="tile">
          <h3>Brand Pillars</h3>
          <p>Sovereignty • Mythic Engineering • Cosmic Precision</p>
        </div>
      </section>
    </div>
  )
}

function AtlantiplexLoginSignup({ onLogin, onSignup, onGotoProduct }) {
  const [tab, setTab] = useState('login')
  const [email, setEmail] = useState('')
  const [pass, setPass] = useState('')
  const [name, setName] = useState('')

  return (
    <div className="atlantiplex-container">
      <nav className="atlantiplex-tabs" aria-label="Atlantiplex tabs">
        <button onClick={() => setTab('home')} className={tab==='home'?'active':''}>Home</button>
        <button onClick={() => setTab('login')} className={tab==='login'?'active':''}>Login</button>
        <button onClick={() => setTab('signup')} className={tab==='signup'?'active':''}>Sign Up</button>
        <button onClick={() => setTab('product')} className={tab==='product'?'active':''}>Product</button>
      </nav>
      {tab==='home' && (
        <div className="atlantiplex-home">
          <p>Atlantiplex Studio is coming soon. Sign in to access the free tier and upgrade later from the product page.</p>
          <button onClick={() => onGotoProduct()} className="holo-button">Go to Product Page</button>
        </div>
      )}
      {tab==='login' && (
        <form className="login-form" onSubmit={(e)=>{e.preventDefault(); onLogin(email);}}>
          <input placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} />
          <input placeholder="Password" type="password" value={pass} onChange={e=>setPass(e.target.value)} />
          <button type="submit" className="holo-button">Login</button>
        </form>
      )}
      {tab==='signup' && (
        <form className="signup-form" onSubmit={(e)=>{e.preventDefault(); onSignup(name, email);}}>
          <input placeholder="Name" value={name} onChange={e=>setName(e.target.value)} />
          <input placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} />
          <button type="submit" className="holo-button">Sign Up</button>
        </form>
      )}
      {tab==='product' && (
        <div className="product-cta">
          <p>Choose a plan below to upgrade your Atlantiplex Studio experience.</p>
          <button className="holo-button" onClick={()=>onGotoProduct()}>Open Product Page</button>
        </div>
      )}
    </div>
  )
}

function ProductPage({ onBuy }) {
  const plans = [
    {id:'free', name:'Free', price:0},
    {id:'starter', name:'Starter', price:9},
    {id:'pro', name:'Pro', price:29}
  ]
  const [selection, setSelection] = useState('free')
  return (
    <section className="product-page" aria-label="Atlantiplex Product">
      <h2>Atlantiplex Studio Plans</h2>
      <div className="cards">
        {plans.map(p => (
          <div key={p.id} className={`card ${selection===p.id?'selected':''}`} onClick={()=>setSelection(p.id)}>
            <h3>{p.name}</h3>
            <p>{p.price===0?'Free':'$'+p.price+'/mo'}</p>
            <button className="holo-button" onClick={(e)=>{e.stopPropagation(); onBuy(p.id);}}>Select</button>
          </div>
        ))}
      </div>
      <div className="note">Upgrade anytime from the Atlantean Studio product page or direct support.</div>
    </section>
  )
}

export default function App(){
  // simple hash-based routing for a demo
  const [route, setRoute] = useState(window.location.hash || '#home')
  useEffect(()=>{
    const onHash = ()=> setRoute(window.location.hash || '#home')
    window.addEventListener('hashchange', onHash)
    return ()=> window.removeEventListener('hashchange', onHash)
  },[])

  const navigate = (hash)=>{ window.location.hash = hash }

  // ATLANTIPLEX auth state in memory/localStorage
  const [user, setUser] = useState(null)
  const [tier, setTier] = useState(null)
  useEffect(()=>{ try { const u = JSON.parse(localStorage.getItem('aa_atlantiplex_user')||'null'); if(u){ setUser(u); setTier(u.tier||'Free'); } } catch(e){} },[])
  const loginUser = (email)=>{ const u={email, tier:'Free'}; localStorage.setItem('aa_atlantiplex_user', JSON.stringify(u)); setUser(u); setTier('Free'); navigate('#atlantiplex'); }
  const signupUser = (name, email)=>{ const u={name, email, tier:'Free'}; localStorage.setItem('aa_atlantiplex_user', JSON.stringify(u)); setUser(u); setTier('Free'); navigate('#atlantiplex'); }
  const goProduct = ()=> navigate('#atlantiplex/product')
  const buyProduct = (plan)=>{
    localStorage.setItem('aa_atlantiplex_subscription', plan);
    navigate('#atlantiplex/product/success')
  }

  let content = null
  if (route.startsWith('#atlantiplex')) {
    content = (
      <div className="atlantiplex">
        <h1>Atlantiplex Studio</h1>
        <p>Welcome, {(user&&user.email)||'Guest'}. Tier: {tier||'Free'}</p>
        <AtlantiplexLoginSignup onLogin={loginUser} onSignup={signupUser} onGotoProduct={goProduct} />
        {route === '#atlantiplex/product' && (
          <ProductPage onBuy={buyProduct} />
        )}
        {route === '#atlantiplex/product/success' && (
          <div className="success">Thanks! Your Atlantiplex Studio free tier is active. Upgrade on the product page.</div>
        )}
      </div>
    )
  } else {
    content = (
      <HomeView onNavigate={(h)=> navigate(h)} />
    )
  }

  return (
    <div className="app-root">
      <header className="site-header" style={{position:'sticky', top:0}}>
        <div className="brand" aria-label="Brand logos area">
          <img src={"../../brand-site/assets/logo-spiral-eye.svg"} alt="Spiral Eye" height={40} />
        </div>
        <nav className="main-nav" aria-label="Main navigation">
          <a href="#home" onClick={(e)=>{e.preventDefault(); navigate('#home')}}>Home</a>
          <a href="#atlantiplex" onClick={(e)=>{e.preventDefault(); navigate('#atlantiplex')}}>Atlantiplex</a>
        </nav>
      </header>
      <main>
        {content}
      </main>
    </div>
  )
}
