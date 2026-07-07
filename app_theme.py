"""Visual theme for VAJRA (Gradio): CSS, theme-toggle JS, masthead.

Cosmetic only — no component IDs or structure depend on this file.
Palette: white canvas · navy command panels · amber accent (military / HUD).
"""

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Rajdhani:wght@500;600;700&family=Inter:wght@400;500;600&family=Crimson+Pro:ital,wght@1,400;1,500&display=swap');

:root{
  --bg:#eef1f6; --bg-soft:#e6ebf2; --card:#ffffff;
  --navy:#173a5e; --navy-2:#1f4d7d; --navy-deep:#0f2740;
  --amber:#f5a623; --amber-deep:#dd8709; --amber-soft:rgba(245,166,35,.15);
  --ink:#15202e; --muted:#5c6b7e; --tagline:#98a2b3;
  --border:#d7dee7; --border-strong:#c1cad6;
  --ok:#1f9d55; --err:#d64545; --warn:#dd8709;
  --radius:6px; --radius-lg:10px;
  --shadow:0 8px 24px rgba(14,37,64,.10);
  --shadow-sm:0 2px 8px rgba(14,37,64,.08);
  --transition:all .18s cubic-bezier(.4,0,.2,1);
}
:root[data-theme="dark"]{
  --bg:#0a1420; --bg-soft:#0c1a29; --card:#102135;
  --navy:#143a60; --navy-2:#1d5085; --navy-deep:#070f19;
  --ink:#e9eff6; --muted:#93a1b3; --tagline:#7f8ba0;
  --border:#1f3550; --border-strong:#2c445f;
  --shadow:0 10px 30px rgba(0,0,0,.55); --shadow-sm:0 2px 10px rgba(0,0,0,.4);
}

*,*::before,*::after{box-sizing:border-box;}
body,.gradio-container{
  background:var(--bg)!important; color:var(--ink)!important;
  font-family:'Inter',system-ui,sans-serif!important; transition:var(--transition);
}
.gradio-container{max-width:100%!important;}

/* ── Masthead ─────────────────────────────────────────────────────────── */
.vajra-masthead{
  position:relative; background:var(--card);
  border-bottom:1px solid var(--border);
  box-shadow:var(--shadow-sm); overflow:hidden;
}
.vajra-masthead::before{  /* faint tactical grid */
  content:''; position:absolute; inset:0; pointer-events:none; opacity:.5;
  background-image:linear-gradient(var(--border) 1px,transparent 1px),
    linear-gradient(90deg,var(--border) 1px,transparent 1px);
  background-size:44px 44px; mask-image:linear-gradient(90deg,transparent,#000 40%,transparent);
}
.vj-rail{position:absolute; left:0; top:0; bottom:0; width:10px;
  background:linear-gradient(180deg,var(--amber),var(--amber-deep)); z-index:2;}
.vj-inner{position:relative; z-index:3; display:flex; align-items:center;
  justify-content:space-between; gap:28px; padding:26px 40px 24px 56px; flex-wrap:wrap;}
.vj-brand{position:relative;}
.vj-wordmark{
  font-family:'Oswald',sans-serif; font-weight:700;
  font-size:clamp(3rem,7vw,5.4rem); line-height:.9; letter-spacing:.16em;
  color:var(--amber); text-shadow:2px 3px 0 rgba(15,39,64,.16); display:block;
}
.vj-brand::after{content:''; display:block; width:118px; height:4px; margin-top:10px;
  background:linear-gradient(90deg,var(--amber),transparent);}
.vj-tagline{font-family:'Crimson Pro',Georgia,serif; font-style:italic;
  font-size:1.18rem; color:var(--tagline); margin-top:12px; display:block;}
.vj-subtitle{font-family:'Rajdhani',sans-serif; font-weight:600; font-size:.9rem;
  letter-spacing:.04em; text-transform:uppercase; color:var(--amber-deep);
  margin-top:8px; max-width:620px; display:block; line-height:1.45;}

.vj-stats{display:grid; grid-template-columns:1fr 1fr; gap:8px; align-content:center;}
.vj-chip{background:var(--navy); color:var(--amber);
  font-family:'Rajdhani',sans-serif; font-weight:600; font-size:.72rem;
  letter-spacing:.09em; text-transform:uppercase; text-align:center;
  padding:11px 18px; border-radius:8px; border:1px solid rgba(255,255,255,.07);
  box-shadow:0 3px 10px rgba(14,37,64,.20); transition:var(--transition);}
.vj-chip:hover{background:var(--navy-2); transform:translateY(-1px);}
.vj-toggle-wrap{grid-column:1/-1; display:flex; justify-content:flex-end; margin-top:2px;}
.vj-toggle{background:transparent; border:1.5px solid var(--navy);
  color:var(--navy); font-family:'Rajdhani',sans-serif; font-weight:600;
  font-size:.62rem; letter-spacing:.12em; text-transform:uppercase;
  padding:5px 14px; border-radius:20px; cursor:pointer; transition:var(--transition);}
.vj-toggle:hover{background:var(--navy); color:#fff;}
:root[data-theme="dark"] .vj-toggle{border-color:var(--amber); color:var(--amber);}

/* ── Tabs (navy command bar, amber active) ────────────────────────────── */
.tab-nav{background:var(--navy-deep)!important; border:none!important;
  border-bottom:3px solid var(--amber)!important; padding:0 16px!important;
  display:flex!important; flex-wrap:wrap!important; gap:2px!important;}
.tab-nav button{font-family:'Rajdhani',sans-serif!important; font-weight:600!important;
  font-size:.82rem!important; letter-spacing:.09em!important; text-transform:uppercase!important;
  color:#a7b8cc!important; background:transparent!important; border:none!important;
  border-bottom:3px solid transparent!important; margin-bottom:-3px!important;
  padding:13px 17px!important; transition:var(--transition)!important;}
.tab-nav button:hover{color:#fff!important; background:rgba(255,255,255,.06)!important;}
.tab-nav button.selected{color:var(--navy-deep)!important; background:var(--amber)!important;
  border-bottom-color:var(--amber)!important; font-weight:700!important;}

/* ── Cards / panels ───────────────────────────────────────────────────── */
.gr-panel,.gr-group,.gr-box,.block,.form,.gr-accordion{
  background:var(--card)!important; border:1px solid var(--border)!important;
  border-radius:var(--radius-lg)!important; box-shadow:var(--shadow-sm)!important;
  transition:var(--transition)!important;}
.gr-group:hover,.gr-panel:hover{border-color:var(--border-strong)!important;}

/* Accordion headers (Media Studio) */
.gr-accordion .label-wrap,.gr-accordion span.label-wrap{
  font-family:'Rajdhani',sans-serif!important; font-weight:600!important;
  text-transform:uppercase!important; letter-spacing:.06em!important;
  color:var(--navy)!important; font-size:.9rem!important;}
:root[data-theme="dark"] .gr-accordion .label-wrap{color:var(--amber)!important;}

/* ── Section labels (custom) ──────────────────────────────────────────── */
.section-label{font-family:'Rajdhani',sans-serif!important; font-weight:700!important;
  font-size:.68rem!important; letter-spacing:.16em!important; text-transform:uppercase!important;
  color:var(--navy)!important; margin-bottom:14px!important;
  display:flex!important; align-items:center!important; gap:9px!important;}
.section-label::before{content:''; width:16px; height:3px; background:var(--amber); flex:0 0 auto;}
.section-label::after{content:''; flex:1; height:1px;
  background:linear-gradient(90deg,var(--border-strong),transparent);}
:root[data-theme="dark"] .section-label{color:var(--amber)!important;}

/* ── Form controls ────────────────────────────────────────────────────── */
label,.gr-label{font-family:'Rajdhani',sans-serif!important; font-weight:600!important;
  font-size:.72rem!important; letter-spacing:.08em!important; text-transform:uppercase!important;
  color:var(--muted)!important;}
textarea,input[type=text],input[type=number],select,.gr-input,.gr-text-input{
  background:var(--bg-soft)!important; border:1px solid var(--border-strong)!important;
  border-radius:var(--radius)!important; color:var(--ink)!important;
  font-family:'Inter',sans-serif!important; font-size:.94rem!important;
  padding:10px 13px!important; transition:var(--transition)!important;}
textarea:focus,input:focus,select:focus{
  border-color:var(--amber)!important; background:var(--card)!important;
  box-shadow:0 0 0 3px var(--amber-soft)!important; outline:none!important;}
input[type=range]{accent-color:var(--amber)!important; height:4px!important;}
input[type=checkbox],input[type=radio]{accent-color:var(--amber)!important; width:16px; height:16px;}

/* ── Buttons ──────────────────────────────────────────────────────────── */
.gr-button{font-family:'Rajdhani',sans-serif!important; font-weight:700!important;
  font-size:.78rem!important; letter-spacing:.11em!important; text-transform:uppercase!important;
  border-radius:var(--radius)!important; transition:var(--transition)!important;}
button.primary,.gr-button.primary{
  background:var(--amber)!important; color:var(--navy-deep)!important; border:none!important;
  padding:12px 26px!important; box-shadow:0 4px 14px rgba(245,166,35,.35)!important;}
button.primary:hover{filter:brightness(1.06)!important; transform:translateY(-1px)!important;
  box-shadow:0 7px 20px rgba(245,166,35,.45)!important;}
button.primary:active{transform:translateY(0)!important;}
button.secondary,.gr-button.secondary{
  background:transparent!important; color:var(--navy)!important;
  border:1.5px solid var(--navy)!important;}
button.secondary:hover{background:var(--navy)!important; color:#fff!important;}
:root[data-theme="dark"] button.secondary{color:var(--amber)!important; border-color:var(--amber)!important;}

/* ── Status / info ────────────────────────────────────────────────────── */
.status-ok{font-family:'Rajdhani',sans-serif; font-weight:600; color:var(--ok); letter-spacing:.05em; text-transform:uppercase; font-size:.8rem;}
.status-err{font-family:'Rajdhani',sans-serif; font-weight:600; color:var(--err); letter-spacing:.05em; text-transform:uppercase; font-size:.8rem;}
.status-warn{font-family:'Rajdhani',sans-serif; font-weight:600; color:var(--warn); letter-spacing:.05em; text-transform:uppercase; font-size:.8rem;}
.audio-info{font-family:'Rajdhani',sans-serif; font-weight:600; font-size:.72rem;
  letter-spacing:.06em; padding:8px 13px; border-radius:var(--radius);
  background:var(--bg-soft); border:1px solid var(--border); border-left:3px solid var(--amber);
  color:var(--muted); margin:4px 0;}

/* ── Output media ─────────────────────────────────────────────────────── */
.output-media img,.output-media video{border-radius:var(--radius)!important;
  border:1px solid var(--border)!important; box-shadow:var(--shadow)!important;}

/* ── Footer ───────────────────────────────────────────────────────────── */
.vram-footer{background:var(--navy-deep); border-top:2px solid var(--amber);
  padding:10px 26px; display:flex; align-items:center; justify-content:space-between;}
.vram-text{font-family:'Rajdhani',sans-serif; font-weight:600; font-size:.66rem;
  letter-spacing:.13em; text-transform:uppercase; color:#9db4d0;}
.vram-accent{color:var(--amber);}

::-webkit-scrollbar{width:9px; height:9px;}
::-webkit-scrollbar-track{background:var(--bg-soft);}
::-webkit-scrollbar-thumb{background:var(--border-strong); border-radius:5px;}
::-webkit-scrollbar-thumb:hover{background:var(--amber);}

@keyframes fadeSlideUp{from{opacity:0; transform:translateY(10px);} to{opacity:1; transform:translateY(0);}}
.gradio-container>*{animation:fadeSlideUp .35s cubic-bezier(.4,0,.2,1) both;}
"""

THEME_JS = """
function vajraToggle(){
  const root=document.documentElement;
  const btn=document.getElementById('vajra-theme-btn');
  if(root.getAttribute('data-theme')==='dark'){
    root.removeAttribute('data-theme'); if(btn) btn.textContent='◐ Dark Mode';
  } else {
    root.setAttribute('data-theme','dark'); if(btn) btn.textContent='☀ Light Mode';
  }
}
"""

MASTHEAD = """
<div class="vajra-masthead">
  <div class="vj-rail"></div>
  <div class="vj-inner">
    <div class="vj-brand">
      <span class="vj-wordmark">VAJRA</span>
      <span class="vj-tagline">Digital Lies. Kinetic Chaos.</span>
      <span class="vj-subtitle">Unified, Offline, Multi-Modal Deep Learning Platform
        for Image, Voice &amp; Video Synthesis</span>
    </div>
    <div class="vj-stats">
      <div class="vj-chip">Image Diffusion</div>
      <div class="vj-chip">Face Swap</div>
      <div class="vj-chip">Voice Clone</div>
      <div class="vj-chip">Video Relip</div>
      <div class="vj-chip">Talking Face</div>
      <div class="vj-chip">Avatar Studio</div>
      <div class="vj-toggle-wrap">
        <button class="vj-toggle" id="vajra-theme-btn" onclick="vajraToggle()">◐ Dark Mode</button>
      </div>
    </div>
  </div>
</div>
"""
