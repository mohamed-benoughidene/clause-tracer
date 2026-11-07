// Clause Tracer prototype: the little behaviour the pages share. No framework, no build.
//   data-open="id"        opens <dialog id="id"> (panels, confirmations, menus as dialogs)
//   data-close            closes the dialog it sits in
//   data-menu="id"        toggles a .menu popover next to the button
//   data-key="J"          pressing that key clicks the element (Ctrl+K opens the command palette)
//   data-toast="text"     shows a short toast
//   data-theme-set="light|dark|system"   switches colours, data-text-set="125" text size (remembered on every page)
//   role="tablist"        tabs switch the panel named in aria-controls
//   .segmented            one pressed button per group
//   data-state="a b"      shown only when the URL has ?state=a (or b); data-state-hide="a" hides it then.
//                         Every state in Spec 14.2 is reachable this way; states.html lists them all.
(function () {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  // ---------------------------------------------------------- appearance: colours and text size (Settings)
  // Saved in localStorage and also in window.name. Opened from disk (file://), some browsers keep a separate
  // localStorage for every file, so window.name is what carries the choice from page to page in the same tab.
  const store = {
    tab() { try { return JSON.parse(window.name || '{}'); } catch (_) { return {}; } },
    get(k) {
      const t = this.tab();
      if (k in t) return t[k];
      try { return localStorage.getItem(k); } catch (_) { return null; }
    },
    set(k, v) {
      const t = this.tab(); t[k] = v;
      try { window.name = JSON.stringify(t); } catch (_) {}
      try { localStorage.setItem(k, v); } catch (_) {}
    },
  };
  function applyTheme(mode) {
    const dark = mode === 'dark' || (mode === 'system' && matchMedia('(prefers-color-scheme: dark)').matches);
    document.documentElement.dataset.theme = dark ? 'dark' : 'light';
    $$('[data-theme-set]').forEach(b => b.setAttribute('aria-pressed', b.dataset.themeSet === mode));
  }
  function applyTextSize(pct) {
    document.body.style.zoom = pct === '100' ? '' : (+pct / 100);
    $$('[data-text-set]').forEach(b => b.setAttribute('aria-pressed', b.dataset.textSet === pct));
    $$('[data-text-label]').forEach(el => { el.textContent = pct + '%'; });
  }
  applyTheme(store.get('ct-theme') || 'system');
  applyTextSize(store.get('ct-text') || '100');
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => applyTheme(store.get('ct-theme') || 'system'));

  // ---------------------------------------------------------- states (Spec 14.2): ?state=name
  const PARAMS = new URLSearchParams(location.search);
  const STATE = PARAMS.get('state') || (PARAMS.has('sample') ? 'sample' : null);   // ?sample is the practice review
  const named = (el, attr) => !!STATE && el.getAttribute(attr).split(/\s+/).includes(STATE);
  $$('[data-state]').forEach(el => el.classList.toggle('on', named(el, 'data-state')));
  $$('[data-state-hide]').forEach(el => { if (named(el, 'data-state-hide')) el.hidden = true; });

  // ---------------------------------------------------------- command palette (same on every page)
  // Opens on the most common commands; each shows its shortcut (Spec 14.4).
  const COMMANDS = [
    ['Review', [['Next unchecked label', 'review.html#next', 'J'], ['Find in contract', 'review.html#find', 'Ctrl+F'],
                ['Suggestions', 'review.html#suggestions', ''], ['Output', 'output.html', '']]],
    ['Go to', [['Reviews', 'home.html', ''], ['New review', 'new-review.html', ''], ['Playbooks', 'playbooks.html', ''],
               ['Customers', 'customers.html', ''], ['Settings', 'settings.html', ''], ['Help', 'help.html', '']]],
    ['Start', [['Try a sample contract', 'review.html?sample', ''], ['First launch', 'index.html', ''],
               ['All prototype states', 'states.html', '']]],
  ];
  document.body.insertAdjacentHTML('beforeend',
    '<dialog id="palette" class="palette" aria-label="Commands"><input type="search" placeholder="Type a command or search…" aria-label="Search commands"><ul>' +
    COMMANDS.map(([g, items]) => '<li><h4>' + g + '</h4><ul>' + items.map(([t, h, k]) =>
      '<li><a href="' + h + '"><span>' + t + '</span>' + (k ? '<kbd>' + k + '</kbd>' : '') + '</a></li>').join('') + '</ul></li>').join('') +
    '</ul><p class="small faint" style="padding:8px 16px;border-top:1px solid var(--line)">↑ ↓ to move · Enter to open · Esc to close</p></dialog>');
  const palette = $('#palette');
  palette.addEventListener('keydown', e => {
    const links = $$('a', palette).filter(a => !a.parentElement.hidden);
    const i = links.indexOf(document.activeElement);
    if (e.key === 'ArrowDown') { e.preventDefault(); (links[i + 1] || links[0]).focus(); }
    if (e.key === 'ArrowUp') { e.preventDefault(); (links[i - 1] || links[links.length - 1]).focus(); }
    if (e.key === 'Enter' && i < 0 && links[0]) { e.preventDefault(); links[0].click(); }
  });
  $('input', palette).addEventListener('input', e => {
    const q = e.target.value.toLowerCase();
    $$('a', palette).forEach(a => { a.parentElement.hidden = !a.textContent.toLowerCase().includes(q); });
  });

  // ---------------------------------------------------------- clicks
  document.addEventListener('click', e => {
    const t = e.target.closest('[data-open],[data-close],[data-menu],[data-toast],[data-theme-set],[data-text-set],.segmented > *,[role="tab"],.search-commands');
    // close open menus on any outside click
    $$('.menu:not([hidden])').forEach(m => { if (!m.contains(e.target) && (!t || t.dataset.menu !== m.id)) m.hidden = true; });
    // click on a dialog's backdrop closes it
    if (e.target.tagName === 'DIALOG') { e.target.close(); return; }
    if (!t) return;
    if (t.classList.contains('search-commands')) { palette.showModal(); return; }
    if (t.dataset.open) { e.preventDefault(); const d = document.getElementById(t.dataset.open); if (d && !d.open) d.showModal(); }
    if (t.hasAttribute('data-close')) { const d = t.closest('dialog'); if (d) d.close(); }
    if (t.dataset.menu) {
      const m = document.getElementById(t.dataset.menu);
      if (m) {
        const r = t.getBoundingClientRect();
        m.style.top = (scrollY + r.bottom + 4) + 'px';
        m.style.left = Math.max(8, Math.min(scrollX + r.right - 220, innerWidth - 228)) + 'px';
        m.hidden = !m.hidden;
      }
    }
    if (t.dataset.toast) toast(t.dataset.toast);
    if (t.dataset.themeSet) { store.set('ct-theme', t.dataset.themeSet); applyTheme(t.dataset.themeSet); }
    if (t.dataset.textSet) { store.set('ct-text', t.dataset.textSet); applyTextSize(t.dataset.textSet); }
    if (t.parentElement && t.parentElement.classList.contains('segmented') && t.tagName === 'BUTTON') {
      $$(':scope > button', t.parentElement).forEach(b => b.setAttribute('aria-pressed', b === t));
    }
    if (t.getAttribute('role') === 'tab') {
      const list = t.closest('[role="tablist"]');
      $$('[role="tab"]', list).forEach(b => {
        const on = b === t;
        b.setAttribute('aria-selected', on);
        const p = document.getElementById(b.getAttribute('aria-controls'));
        if (p) p.hidden = !on;
      });
    }
  });

  // ---------------------------------------------------------- keys
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); palette.open ? palette.close() : palette.showModal(); return; }
    if (e.key === 'Escape') $$('.menu:not([hidden])').forEach(m => { m.hidden = true; });
    if ((e.target.closest && e.target.closest('input, textarea, select, [contenteditable]')) || e.ctrlKey || e.metaKey || e.altKey) return;
    const open = $$('dialog[open]').pop();
    const el = $$('[data-key]', open || document).find(x => x.dataset.key.toLowerCase() === e.key.toLowerCase());
    if (el) { e.preventDefault(); el.click(); }
  });

  // ---------------------------------------------------------- toast
  let timer;
  function toast(text) {
    let t = $('#toast');
    if (!t) { document.body.insertAdjacentHTML('beforeend', '<div id="toast" class="toast" role="status" hidden></div>'); t = $('#toast'); }
    t.textContent = text; t.hidden = false;
    clearTimeout(timer); timer = setTimeout(() => { t.hidden = true; }, 2200);
  }
  window.CT = { toast, applyTheme };

  // open a dialog named in the URL hash (#detail-4) so pages can link straight to a state
  const h = location.hash.slice(1);
  const d = h && document.getElementById(h);
  if (d && d.tagName === 'DIALOG') d.showModal();
})();
