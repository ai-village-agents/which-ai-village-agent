const $ = (id) => document.getElementById(id);

function clamp(x, lo, hi){ return Math.max(lo, Math.min(hi, x)); }

function encode(obj){
  const json = JSON.stringify(obj);
  return btoa(unescape(encodeURIComponent(json))).replaceAll('=', '');
}
function decode(str){
  const pad = str + '==='.slice((str.length + 3) % 4);
  const json = decodeURIComponent(escape(atob(pad)));
  return JSON.parse(json);
}

function dot(a,b){
  let s = 0;
  for (const k of Object.keys(a)) s += (a[k]||0) * (b[k]||0);
  return s;
}
function norm(a){
  return Math.sqrt(dot(a,a)) || 1;
}
function cosine(a,b){
  return dot(a,b) / (norm(a) * norm(b));
}

function emptyVector(dimIds){
  return Object.fromEntries(dimIds.map(d => [d, 0]));
}

function likertToScore(v){
  // v in [1..5] -> [-1..+1]
  return (clamp(v,1,5) - 3) / 2;
}

function computeDimMaxAbs(questions, dimIds){
  // Maximum possible absolute contribution per dimension, given the question weights.
  // Since likertToScore() returns in [-1..+1] and forced_choice uses {-1,+1},
  // each question can contribute at most |w| to a dimension.
  const maxAbs = Object.fromEntries(dimIds.map(d => [d, 0]));
  for (const q of questions){
    for (const [dim, w] of Object.entries(q.weights)){
      if (maxAbs[dim] == null) maxAbs[dim] = 0;
      maxAbs[dim] += Math.abs(w);
    }
  }
  return maxAbs;
}

function computeVector(answers, questions, dimIds){
  const vec = emptyVector(dimIds);
  for (const q of questions){
    const a = answers[q.id];
    if (a == null) continue;

    if (q.type === 'likert'){
      const s = likertToScore(a);
      for (const [dim, w] of Object.entries(q.weights)) vec[dim] += s * w;
    } else if (q.type === 'forced_choice'){
      // a is 0 or 1.
      // By default Option1 is treated as the "positive" direction (+1).
      // Some questions invert this via option1IsPositive=false (meaning Option0 is +1).
      const option1IsPositive = (q.option1IsPositive !== false);
      const s = option1IsPositive ? ((a === 1) ? 1 : -1) : ((a === 0) ? 1 : -1);
      for (const [dim, w] of Object.entries(q.weights)) vec[dim] += s * w;
    }
  }

  // Normalize into per-dimension [-1..+1] for both display and matching.
  // (Avoids the prior global-max normalization, which distorted relative dimensions
  // and made cosine matching unstable.)
  const maxAbs = computeDimMaxAbs(questions, dimIds);
  for (const k of Object.keys(vec)){
    const denom = maxAbs[k] || 0;
    vec[k] = denom ? clamp(vec[k] / denom, -1, 1) : 0;
  }
  return vec;
}

function agentVectorToPm1(agentVec, dimIds){
  // Agent vectors are *ideally* stored in [0..1] per dimension.
  // Convert to [-1..+1] so they live in the same space as the quiz output.
  //
  // Compatibility: if an agent value is already outside [0..1], treat it as already
  // being in [-1..+1] and clamp. (This avoids accidental "double mapping".)
  const out = {};
  for (const d of dimIds){
    const v = agentVec[d];
    if (v == null) out[d] = 0;
    else if (v >= 0 && v <= 1) out[d] = (v - 0.5) * 2;
    else out[d] = clamp(v, -1, 1);
  }
  return out;
}

function bestMatch(vec, agents, dimIds){
  let best = null;
  for (const a of agents){
    const score = cosine(vec, agentVectorToPm1(a.vector, dimIds));
    if (!best || score > best.score) best = { agent: a, score };
  }
  return best;
}

function generateBadgesHTML(vec, dimById){
  // Guard against missing or unknown dimensions when constructing badges.
  // (Fixes crash when vectors contain keys not in dimensions.json - see PR #40)
  return Object.keys(vec).filter(k => dimById[k]).map(id => {
    const d = dimById[id];
    const v = vec[id];
    const label = v >= 0 ? d.right : d.left;
    const pct = Math.round(Math.abs(v) * 100);
    return `<span class="badge">${d.label}: ${label} (${pct}%)</span>`;
  }).join('');
}

function updateAddressBar(shareUrl){
  try {
    const relativeUrl = shareUrl.pathname + shareUrl.search + shareUrl.hash;
    history.replaceState(null, '', relativeUrl);
  } catch (err) {
    console.warn('Failed to update address bar to share URL', err);
  }
}

function generateSocialLinks(agent, shareUrl){
  const share = shareUrl.toString();
  const postText = `I matched with ${agent.name}! ${agent.tagline}\n\nFind out which AI Village agent you are:`;
  const twitterUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(postText)}&url=${encodeURIComponent(share)}`;
  const linkedinUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(share)}`;
  const encodedText = encodeURIComponent(`${postText}\n${share}`);
  const blueskyUrl = `https://bsky.app/intent/compose?text=${encodedText}`;
  return { twitterUrl, linkedinUrl, blueskyUrl };
}

const repoRootPath = (() => {
  const { pathname } = window.location;
  const shareRoute = pathname.match(/^(.*\/)r\/[^/]+\/?(?:index\.html)?$/);
  if (shareRoute) return shareRoute[1];
  if (pathname.endsWith('/')) return pathname;
  return pathname.replace(/\/[^/]*$/, '/');
})();

function renderResult({agent, score, vec, dimensions}){
  const dimById = Object.fromEntries(dimensions.map(d => [d.id, d]));

  const badges = generateBadgesHTML(vec, dimById);

  const share = new URL(`${repoRootPath}r/${encodeURIComponent(agent.id)}/`, window.location.href);
  share.searchParams.set('v', encode(vec));
  updateAddressBar(share);
  const { twitterUrl, linkedinUrl, blueskyUrl } = generateSocialLinks(agent, share);
  const shareUrl = share.toString();
  const issueUrl = 'https://github.com/ai-village-agents/which-ai-village-agent/issues/36#issuecomment-new';
  const issueBody = `I took the Which AI Village Agent Are You? quiz and matched with ${agent.name}.\n${shareUrl}\n\nWhat did you get?`;
  const shareHelpUrl = `${repoRootPath}share/`;
  const commentText = issueBody;

  $('result').innerHTML = `
    <h2>Your match: ${agent.name}</h2>
    <p class="sub">${agent.tagline}</p>
    <div>${badges}</div>
    <div class="hr"></div>

    <h3>Why this match</h3>
    <ul>${agent.why.map(x => `<li>${x}</li>`).join('')}</ul>

    <h3>Strengths</h3>
    <ul>${agent.strengths.map(x => `<li>${x}</li>`).join('')}</ul>

    <h3>Watch-outs</h3>
    <ul>${agent.watchouts.map(x => `<li>${x}</li>`).join('')}</ul>

    <div class="hr"></div>
    <div class="share-heading">
      <div>
        <h3>Share your result</h3>
        <p class="small">Copy this link:</p>
      </div>
      <p class="small"><a href="${shareHelpUrl}">Need help sharing?</a></p>
    </div>
    <div class="code">${shareUrl}</div>

    <div class="cta-row push-top">
      <button id="copyShareBtn">Copy share link</button>
      <button id="copyCommentBtn" class="secondary">Copy GitHub comment</button>
      <a href="${issueUrl}" target="_blank" rel="noreferrer"><button>Post to GitHub (Issue #36)</button></a>
      <a href="${shareUrl}" target="_blank" rel="noreferrer"><button class="secondary">Open share link</button></a>
    </div>
    <p class="small">GitHub comment includes your agent name, share link, and "What did you get?"</p>

    <div class="nav" style="margin-top:14px">
      <button id="restartBtn" class="secondary">Restart</button>
      <a href="${twitterUrl}" target="_blank" rel="noreferrer"><button>Share on X</button></a>
      <a href="${blueskyUrl}" target="_blank" rel="noreferrer"><button>Share on Bluesky</button></a>
      <a href="${linkedinUrl}" target="_blank" rel="noreferrer"><button>Share on LinkedIn</button></a>
    </div>
    <p class="small">Note: this is a beta scoring model; agent portrayals will be updated after sign-off.</p>
  `;

  const copyWithFallback = async (text, fallbackLabel) => {
    if (navigator?.clipboard?.writeText){
      try {
        await navigator.clipboard.writeText(text);
        return true;
      } catch (err){
        console.warn('Clipboard write failed, falling back to prompt', err);
      }
    }
    const res = window.prompt(fallbackLabel, text);
    if (res === null){
      alert('Copy failed. Please manually copy the text.');
      return false;
    }
    return true;
  };

  const copyShareBtn = $('copyShareBtn');
  if (copyShareBtn){
    copyShareBtn.addEventListener('click', async () => {
      const ok = await copyWithFallback(shareUrl, 'Copy this share link');
      if (ok){
        copyShareBtn.textContent = 'Copied!';
        setTimeout(() => copyShareBtn.textContent = 'Copy share link', 1400);
      }
    });
  }

  const copyCommentBtn = $('copyCommentBtn');
  if (copyCommentBtn){
    copyCommentBtn.addEventListener('click', async () => {
      const ok = await copyWithFallback(commentText, 'Copy this GitHub comment');
      if (ok){
        copyCommentBtn.textContent = 'Copied!';
        setTimeout(() => copyCommentBtn.textContent = 'Copy GitHub comment', 1400);
      }
    });
  }

  $('restartBtn').addEventListener('click', () => {
    window.location.href = repoRootPath;
  });
}

async function main(){
  const cacheBust = (typeof window !== 'undefined' && window.__AV_CACHE_BUST)
    ? window.__AV_CACHE_BUST
    : Date.now().toString();

  const [dims, qs, agentsData] = await Promise.all([
    fetch(`data/dimensions.json?v=${cacheBust}`, { cache: 'no-store' }).then(r=>r.json()),
    fetch(`data/questions.json?v=${cacheBust}`, { cache: 'no-store' }).then(r=>r.json()),
    fetch(`data/agents.json?v=${cacheBust}`, { cache: 'no-store' }).then(r=>r.json())
  ]);

  const dimensions = dims.dimensions;
  const questions = qs.questions;
  const dimIds = qs.dimensions;
  const agents = agentsData.agents;

  $('loading').classList.add('hidden');

  // Share link mode
  const currentUrl = new URL(window.location.href);
  const params = currentUrl.searchParams;
  const pathAgentMatch = currentUrl.pathname.match(/\/r\/([^/]+)\/?(?:index\.html)?$/);
  const r = params.get('r') ?? (pathAgentMatch ? decodeURIComponent(pathAgentMatch[1]) : null);
  const v = params.get('v');
  if (r && v){
    const agent = agents.find(a => a.id === r);
    if (agent){
      const vec = decode(v);
      $('result').classList.remove('hidden');
      renderResult({agent, score: 1, vec, dimensions});
      return;
    }
  }

  $('start').classList.remove('hidden');

  let idx = 0;
  const answers = {};
  let currentSelection = null;

  function setSelection(sel){
    currentSelection = sel;
    for (const el of document.querySelectorAll('.option')){
      el.classList.toggle('selected', el.dataset.value == String(sel));
    }
    $('nextBtn').disabled = (sel == null);
  }

  function renderQuestion(){
    const q = questions[idx];
    $('quiz').classList.remove('hidden');
    $('start').classList.add('hidden');
    $('result').classList.add('hidden');

    $('progress').textContent = `Question ${idx+1} / ${questions.length}`;
    $('prompt').textContent = q.prompt;

    $('backBtn').disabled = idx === 0;
    $('nextBtn').textContent = (idx === questions.length-1) ? 'Finish' : 'Next';

    const optionsEl = $('options');
    optionsEl.innerHTML = '';

    if (q.type === 'likert'){
      const labels = [
        'Strongly disagree',
        'Disagree',
        'Neutral',
        'Agree',
        'Strongly agree'
      ];
      labels.forEach((lab, i) => {
        const v = i+1;
        const div = document.createElement('div');
        div.className = 'option';
        div.dataset.value = String(v);
        div.textContent = lab;
        div.addEventListener('click', () => setSelection(v));
        optionsEl.appendChild(div);
      });
    } else {
      q.options.forEach((lab, i) => {
        const div = document.createElement('div');
        div.className = 'option';
        div.dataset.value = String(i);
        div.textContent = lab;
        div.addEventListener('click', () => setSelection(i));
        optionsEl.appendChild(div);
      });
    }

    const prev = answers[q.id];
    currentSelection = prev ?? null;
    setSelection(currentSelection);
  }

  function finish(){
    const vec = computeVector(answers, questions, dimIds);
    const match = bestMatch(vec, agents, dimIds);

    $('quiz').classList.add('hidden');
    $('result').classList.remove('hidden');
    renderResult({agent: match.agent, score: match.score, vec, dimensions});
  }

  $('startBtn').addEventListener('click', () => renderQuestion());

  $('backBtn').addEventListener('click', () => {
    const q = questions[idx];
    if (currentSelection != null) answers[q.id] = currentSelection;
    idx = Math.max(0, idx-1);
    currentSelection = answers[questions[idx].id] ?? null;
    renderQuestion();
  });

  $('nextBtn').addEventListener('click', () => {
    const q = questions[idx];
    if (currentSelection == null) return;
    answers[q.id] = currentSelection;

    if (idx === questions.length-1) return finish();
    idx += 1;
    currentSelection = null;
    renderQuestion();
  });
}

main().catch(err => {
  console.error(err);
  $('loading').classList.remove('hidden');
  $('loading').innerHTML = `<p style="color: var(--danger)">Failed to load quiz data. Open console for details.</p>`;
});
