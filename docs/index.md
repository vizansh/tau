---
title: Tau
description: A minimalist coding-agent harness in Python.
hide:
  - navigation
  - toc
  - edit
---

<div class="tau-landing">
<div class="wrap">
  <nav>
    <div class="brand">
      <span class="glyph">&#964;</span>
      <span class="name">tau</span>
      <span class="ver">v0.1</span>
    </div>
    <div class="navlinks">
      <a href="getting-started/">Docs</a>
      <a href="https://github.com/alejandro-ao/tau/issues/1">Roadmap</a>
      <a href="#start">Getting started</a>
      <a class="gh" href="https://github.com/alejandro-ao/tau">GitHub &#8599;</a>
    </div>
  </nav>

  <header>
    <div class="hero-grid">
      <div>
        <p class="eyebrow">A minimalist coding-agent harness</p>
        <h1>A coding agent<br />small enough to <em>read.</em></h1>
        <p class="lede">
          <strong>Tau</strong> is a terminal coding agent in Python &mdash; and a
          phase-by-phase reference for how one is actually built. Named for
          <span class="tau">&#964;</span>&#8202;=&#8202;2&#960;: one full turn,
          nothing hidden.
        </p>
        <div class="cta-row">
          <span class="install">
            <span><span class="dollar">$</span> uv tool install tau</span>
            <button class="copy" id="copyBtn" type="button" aria-label="Copy install command">copy</button>
          </span>
          <a class="ghost" href="getting-started/">Read the docs <span class="arr">&rarr;</span></a>
        </div>
      </div>

      <figure class="figure">
        <span class="figlabel">&#952; sweeps 0 &rarr; &#964;</span>
        <canvas id="tauCanvas" width="520" height="380" role="img"
          aria-label="A radius sweeping a unit circle through one full turn, tracing one period of a sine wave on notebook paper."></canvas>
        <span class="figval" id="thetaVal">&#952; = 0.00</span>
      </figure>
    </div>

    <div class="strip">
      <div class="cellitem"><span class="num">&#964;&#8202;=&#8202;6.283&#8230;</span><span class="cap">one full turn</span></div>
      <div class="cellitem"><span class="num">3</span><span class="cap">small layers</span></div>
      <div class="cellitem"><span class="num">0</span><span class="cap">magic</span></div>
    </div>
  </header>
</div>

<div class="wrap">
  <section id="start">
    <div class="sec-head">
      <span class="mark">01</span>
      <h2>Three layers, each explainable on its own</h2>
    </div>
    <div class="layers">
      <div class="layer">
        <span class="idx">&#8544;</span>
        <span class="pkg">tau_ai</span>
        <h3>The provider</h3>
        <p>Models stream events. A thin layer turns provider responses into a single, ordered event stream you can follow line by line.</p>
      </div>
      <div class="layer">
        <span class="idx">&#8545;</span>
        <span class="pkg">tau_agent</span>
        <h3>The harness</h3>
        <p>A portable brain: the loop that turns events into tool calls, owns transcript and session state, and stays free of any one app.</p>
      </div>
      <div class="layer">
        <span class="idx">&#8546;</span>
        <span class="pkg">tau_coding</span>
        <h3>The agent</h3>
        <p>Files, shell, sessions, skills, commands, and a terminal UI &mdash; one concrete coding environment built on the harness.</p>
      </div>
    </div>
  </section>

  <section>
    <div class="two">
      <div>
        <p class="eyebrow">The boundary</p>
        <h2>A reusable brain, a swappable body.</h2>
        <p>The <span class="tau">&#964;</span> harness is the agent. The session is its environment. The terminal is just one possible face. Keep them apart and the whole thing stays legible.</p>
      </div>
      <div class="terminal" aria-hidden="true">
        <div class="bar"><span></span><span></span><span></span><span class="t">tau &mdash; session</span></div>
        <pre><span class="pmt">&#964; &rsaquo;</span> <span class="cmd">fix the failing test in parser.py</span>

<span class="out">  reading  </span><span class="key">parser.py</span><span class="out">, </span><span class="key">test_parser.py</span>
<span class="out">  edit     </span><span class="key">parser.py</span><span class="out">  +4 &minus;1</span>
<span class="out">  run      </span><span class="key">uv run pytest -q</span>
<span class="out">  &check; 1 passed in 0.21s</span>

<span class="pmt">&#964; &rsaquo;</span> <span class="cmd">_</span></pre>
      </div>
    </div>
  </section>

  <section>
    <div class="sec-head">
      <span class="mark">02</span>
      <h2>The philosophy</h2>
    </div>
    <div class="principles">
      <div class="pr">
        <h3>Small layers beat magic</h3>
        <p>Every package has one job and can be explained without the others. No framework you have to believe in.</p>
      </div>
      <div class="pr">
        <h3>Explicit over clever</h3>
        <p>The control flow is on the page. Streaming, tool calls, sessions &mdash; readable top to bottom.</p>
      </div>
      <div class="pr">
        <h3>Built phase by phase</h3>
        <p>Each commit adds one understandable piece, so the repo doubles as a course in how agents are assembled.</p>
      </div>
      <div class="pr">
        <h3>Usable, not just instructive</h3>
        <p>It is a real terminal agent you can run today &mdash; the teaching is a side effect of the design, not a toy.</p>
      </div>
    </div>
  </section>

  <section class="closing">
    <span class="turn">&#964;</span>
    <p>Start the loop. Watch a coding agent run with nothing hidden between you and the code.</p>
    <div class="cta-row">
      <span class="install">
        <span><span class="dollar">$</span> uv tool install tau</span>
        <button class="copy" id="copyBtn2" type="button" aria-label="Copy install command">copy</button>
      </span>
      <a class="ghost" href="https://github.com/alejandro-ao/tau">View on GitHub <span class="arr">&rarr;</span></a>
    </div>
  </section>

  <footer>
    <div class="brand">
      <span class="glyph" style="font-size:20px;">&#964;</span>
      <span class="name">tau</span>
    </div>
    <div class="l">
      <a href="getting-started/">Docs</a>
      <a href="https://github.com/alejandro-ao/tau">GitHub</a>
      <a href="https://github.com/alejandro-ao/tau/issues/1">Roadmap</a>
    </div>
    <span>A teaching project &middot; inspired by Pi</span>
  </footer>
</div>
</div>
