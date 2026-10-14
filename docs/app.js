const $ = (selector) => document.querySelector(selector);
const state = { papers: [], scope: 'all', category: 'all', query: '', sort: 'score' };
const escapeHTML = (value = '') => String(value).replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const mainPaper = (paper) => paper.list_status === 'main' || paper.list_status_recommendation === 'main';
const label = (paper) => mainPaper(paper) ? '主榜' : '观察区';
const scoreClass = (paper) => mainPaper(paper) ? 'main' : '';

function renderFeatured(papers) {
  const featured = papers.filter(mainPaper).slice(0, 3);
  $('#featured').innerHTML = featured.map((p, i) => `
    <article class="featured-item">
      <div class="rank">0${i + 1} / ${escapeHTML(p.source || '论文')}</div>
      <div><h3 class="paper-title"><a href="${escapeHTML((p.urls || ['#'])[0])}" target="_blank" rel="noreferrer">${escapeHTML(p.title)}</a></h3>
        <p class="paper-question">${escapeHTML(p.one_line_question || '')}</p>
        <p class="paper-summary">${escapeHTML(p.summary_zh || '')}</p>
        <div class="paper-meta"><span class="tag main">${label(p)}</span><span class="tag">${escapeHTML(p.category || '未分类')}</span><span class="tag">置信度 ${escapeHTML(p.confidence || '未标注')}</span><span class="tag">${escapeHTML(p.relevance_to_project || '相关性待判')}</span></div></div>
      <div class="score">${Number(p.innovation_score) || 0}<small> /100</small></div>
    </article>`).join('') || '<p class="load-error">本期暂无达到主榜证据标准的论文。</p>';
}

function filteredPapers() {
  const q = state.query.trim().toLocaleLowerCase();
  return state.papers.filter((p) => {
    const matchesScope = state.scope === 'all' || (state.scope === 'main' ? mainPaper(p) : !mainPaper(p));
    const matchesCategory = state.category === 'all' || (p.category || '未分类') === state.category;
    const text = [p.title, p.summary_zh, p.one_line_question, p.category, p.relevance_to_project, ...(p.tags || [])].join(' ').toLocaleLowerCase();
    return matchesScope && matchesCategory && (!q || text.includes(q));
  }).sort((a,b) => state.sort === 'date' ? String(b.last_seen || b.date || '').localeCompare(String(a.last_seen || a.date || '')) : Number(b.innovation_score) - Number(a.innovation_score));
}

function renderList() {
  const items = filteredPapers();
  $('#result-count').textContent = `${items.length} 篇`;
  $('#empty').hidden = items.length > 0;
  $('#paper-list').innerHTML = items.map((p) => `
    <article class="archive-row">
      <div class="archive-date">${escapeHTML(p.date || p.last_seen || '—')}</div>
      <div><h3 class="paper-title"><a href="${escapeHTML((p.urls || ['#'])[0])}" target="_blank" rel="noreferrer">${escapeHTML(p.title)}</a></h3>
        <p class="paper-question">${escapeHTML(p.one_line_question || '')}</p>
        <p class="paper-summary">${escapeHTML(p.summary_zh || '')}</p>
        <div class="paper-meta"><span class="tag ${scoreClass(p)}">${label(p)}</span><span class="tag">${escapeHTML(p.category || '未分类')}</span><span class="tag">${escapeHTML(p.relevance_to_project || '相关性待判')}</span></div>
        <details><summary class="archive-links">查看分项与证据限制</summary><p class="paper-summary">评分分项：${escapeHTML(JSON.stringify(p.score_breakdown || {}))}<br>证据与限制：${escapeHTML(p.evidence_limit || '本条未提供详细证据限制。')}<br>建议动作：${escapeHTML(p.recommended_action || '—')}</p></details>
      </div><div class="score">${Number(p.innovation_score) || 0}<small> /100</small></div>
    </article>`).join('');
}

function setup(data) {
  state.papers = data.papers || [];
  const issues = data.issues || [];
  const latest = issues[0];
  const main = state.papers.filter(mainPaper);
  $('#updated').textContent = data.updated_at ? `最近更新 ${data.updated_at}` : '等待首次周更';
  $('#issue-date').textContent = latest ? `· ${latest.date}` : '';
  if (latest) $('#issue-link').href = latest.url;
  $('#count-total').textContent = state.papers.length;
  $('#count-main').textContent = main.length;
  $('#top-score').textContent = main.length ? Math.max(...main.map(p => Number(p.innovation_score) || 0)) : '—';
  renderFeatured(state.papers);
  const categories = [...new Set(state.papers.map(p => p.category || '未分类'))].sort();
  $('#category').innerHTML += categories.map(c => `<option value="${escapeHTML(c)}">${escapeHTML(c)}</option>`).join('');
  $('#issue-list').innerHTML = issues.map(i => `<a class="issue-link" href="${escapeHTML(i.url)}">${escapeHTML(i.date)}　${i.main_count} 篇主榜　最高 ${i.top_score}</a>`).join('') || '<span class="metric-note">首期周报发布后会显示在这里。</span>';
  renderList();
}

document.querySelectorAll('.segmented button').forEach((button) => button.addEventListener('click', () => {
  document.querySelectorAll('.segmented button').forEach(b => b.classList.remove('selected'));
  button.classList.add('selected'); state.scope = button.dataset.scope; renderList();
}));
$('#search').addEventListener('input', e => { state.query = e.target.value; renderList(); });
$('#category').addEventListener('change', e => { state.category = e.target.value; renderList(); });
$('#sort').addEventListener('change', e => { state.sort = e.target.value; renderList(); });
fetch('./dashboard.json', { cache: 'no-store' }).then(r => { if (!r.ok) throw new Error('dashboard.json unavailable'); return r.json(); }).then(setup).catch(() => {
  $('#featured').innerHTML = '<p class="load-error">暂时无法读取周报数据。请稍后刷新，或前往 GitHub 查看数据文件。</p>';
  $('#updated').textContent = '数据加载失败';
});
