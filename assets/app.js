const BASE_PATH = window.MEAL_PLAN_BASE || '';
const INDEX_URL = `${BASE_PATH}data/weeks/index.json`;

const app = document.querySelector('#app');

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function linkify(text) {
  const escaped = escapeHtml(text);
  return escaped.replace(/https:\/\/[^\s)]+/g, url => `<a href="${url}">${url}</a>`);
}

function list(items = [], className = '') {
  if (!items.length) return '';
  return `<ul class="${className}">${items.map(item => `<li>${linkify(item)}</li>`).join('')}</ul>`;
}

function orderedList(items = []) {
  if (!items.length) return '';
  return `<ol>${items.map(item => `<li>${linkify(item)}</li>`).join('')}</ol>`;
}

function tags(tags = []) {
  return tags.length ? `<div class="tags">${tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}</div>` : '';
}

function weekHref(slug) {
  return `${BASE_PATH}weeks/${encodeURIComponent(slug)}/`;
}

function selectedSlugFromLocation() {
  const requested = new URLSearchParams(window.location.search).get('week');
  if (requested) return requested;

  const match = window.location.pathname.match(/\/weeks\/([^/]+)\/?$/);
  return match ? decodeURIComponent(match[1]) : null;
}

async function fetchJson(path) {
  const response = await fetch(path, { cache: 'no-cache' });
  if (!response.ok) throw new Error(`Failed to load ${path}: HTTP ${response.status}`);
  return response.json();
}

function renderWeekPicker(index, selectedSlug) {
  return `
    <section id="week-list" class="week-picker">
      <h2>Available weeks</h2>
      <div class="week-tabs">
        ${index.weeks.map(week => `
          <a class="week-tab ${week.slug === selectedSlug ? 'active' : ''}" href="${weekHref(week.slug)}">
            ${escapeHtml(week.label)}
          </a>
        `).join('')}
      </div>
      <p class="small">To add another week, copy <code>templates/week-template.json</code> into <code>data/weeks/YYYY-MM-DD.json</code>, add it to <code>data/weeks/index.json</code>, then run <code>python3 scripts/generate_pages.py && python3 scripts/validate.py</code>.</p>
    </section>
  `;
}

function renderSummary(plan) {
  const cards = [
    ['Use first', plan.useFirst],
    ['Use later', plan.useLater],
    ['Time target', plan.timeTarget],
    ['Buy if needed', plan.buyIfNeeded]
  ];
  return `<div class="summary">${cards.map(([title, body]) => `<div><strong>${escapeHtml(title)}</strong>${escapeHtml(body)}</div>`).join('')}</div>`;
}

function renderNotes(notes = []) {
  return notes.map(note => `
    <div class="note">
      <strong>${escapeHtml(note.title)}:</strong> ${linkify(note.body)}
      ${note.source ? `<p class="small">Source: <a href="${escapeHtml(note.source.url)}">${escapeHtml(note.source.label)}</a></p>` : ''}
    </div>
  `).join('');
}

function renderRecipe(day) {
  return `
    <article id="${escapeHtml(day.id)}">
      <div class="eyebrow">${escapeHtml(day.dateLabel)}</div>
      <h2>${escapeHtml(day.title)}</h2>
      <p class="meta">Protein: ${escapeHtml(day.protein)} · Carb: ${escapeHtml(day.carb)} · Veg: ${escapeHtml(day.veg)} · Time: ${escapeHtml(day.time)}</p>
      ${tags(day.tags)}
      ${day.note ? `<div class="note small">${linkify(day.note)}</div>` : ''}
      <div class="grid recipe-section">
        <section>
          <h3>Ingredients</h3>
          ${list(day.ingredients)}
        </section>
        <section>
          <h3>Steps</h3>
          ${orderedList(day.steps)}
          ${day.ariaServing ? `<p class="small"><strong>Aria serving:</strong> ${escapeHtml(day.ariaServing)}</p>` : ''}
        </section>
      </div>
    </article>
  `;
}

function renderPlan(index, plan, selectedSlug) {
  document.title = `${plan.title} — Ruths Weekly Meal Plans`;
  app.innerHTML = `
    ${renderWeekPicker(index, selectedSlug)}
    <section>
      <div class="eyebrow">${escapeHtml(plan.kicker || 'Meal plan')}</div>
      <h2>${escapeHtml(plan.title)}</h2>
      <p>${escapeHtml(plan.description)}</p>
      ${renderSummary(plan)}
      ${renderNotes(plan.notes)}
    </section>
    ${plan.days.map(renderRecipe).join('')}
    <article id="shopping">
      <h2>Small grocery list</h2>
      ${list(plan.groceryList, 'grocery-list')}
    </article>
  `;
}

function renderError(error) {
  app.innerHTML = `
    <section class="error-card">
      <h2>Meal plan could not load</h2>
      <p>${escapeHtml(error.message)}</p>
      <p class="small">Check JSON syntax, generated week pages, and <code>data/weeks/index.json</code>.</p>
    </section>
  `;
}

async function init() {
  try {
    const index = await fetchJson(INDEX_URL);
    const requested = selectedSlugFromLocation();
    const selected = index.weeks.find(week => week.slug === requested) || index.weeks[0];
    const plan = await fetchJson(`${BASE_PATH}${selected.path}`);
    renderPlan(index, plan, selected.slug);
  } catch (error) {
    renderError(error);
    console.error(error);
  }
}

init();
