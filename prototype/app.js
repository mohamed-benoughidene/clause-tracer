// Clause Tracer prototype: the little behaviour the pages share. No framework, no build.
//   data-open="id"        opens <dialog id="id"> (panels, confirmations, menus as dialogs)
//   data-close            closes the dialog it sits in
//   data-menu="id"        toggles a .menu popover next to the button
//   data-key="J"          pressing that key clicks the element (Ctrl+K opens the command palette)
//   data-toast="text"     shows a short toast
//   data-theme-set="light|dark|system"   switches colours, data-text-set="125" text size (remembered on every page)
//   role="tablist"        tabs switch the panel named in aria-controls
//   .segmented            one pressed button per group
//   ol.steps[data-step]   the flow stepper: its line draws in on every load, and the forward button in .flow-foot plays a short leave
//   [data-private-switch] the shared Private mode switch (kept in ct-private; asks first on <dialog id="private-off">)
//   The tab strip (ct-tabs) and the Collapse menu button (ct-sidebar, Ctrl+B) are added here; pages carry no markup for them.
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
    document.documentElement.dataset.text = pct;   // lets styles.css re-flow the layout at 150% and 200%
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

  // ---------------------------------------------------------- window shell: set before the page paints
  // The tab strip is on every page except First launch and the prototype map. The sidebar may be folded (Ctrl+B).
  const PAGE = location.pathname.split('/').pop() || 'index.html';
  const HAS_TABS = PAGE !== 'index.html' && PAGE !== 'states.html' && location.protocol !== 'data:';
  if (HAS_TABS) document.documentElement.classList.add('has-wintabs');
  if (store.get('ct-sidebar') === 'collapsed' || STATE === 'sidebar-collapsed') document.documentElement.dataset.sidebar = 'collapsed';

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

  // ---------------------------------------------------------- Private mode switch (one component, every page)
  // <button class="pm-switch" role="switch" aria-checked data-private-switch>. On is one click. Off asks first when the page
  // has <dialog id="private-off"> whose confirm button has value="ok"; without that dialog it switches off at once.
  function applyPrivate(on) {
    $$('[data-private-switch]').forEach(b => b.setAttribute('aria-checked', on));
    $$('[data-private-text]').forEach(el => { el.textContent = 'Private mode: ' + (on ? 'On' : 'Off'); });
    updateTips();
  }
  const isPrivate = () => store.get('ct-private') !== 'off';
  function setPrivate(on) { store.set('ct-private', on ? 'on' : 'off'); applyPrivate(on); toast(on ? 'Private mode on' : 'Private mode off'); }
  Object.assign(window.CT, { isPrivate, setPrivate });   // for a page that shows private mode without a switch (running)
  document.addEventListener('click', e => {
    const sw = e.target.closest('[data-private-switch]');
    if (!sw) return;
    if (!isPrivate()) { setPrivate(true); return; }
    const ask = document.getElementById('private-off');
    if (!ask || ask.tagName !== 'DIALOG') { setPrivate(false); return; }
    ask.returnValue = '';
    let finished = false;
    const finish = confirmed => {
      if (finished) return;
      finished = true;
      ask.removeEventListener('close', onClose); ask.removeEventListener('click', onClick);
      if (confirmed) setPrivate(false);
    };
    const onClose = () => finish(ask.returnValue === 'ok');
    const onClick = ev => { const b = ev.target.closest('button[value="ok"]'); if (b) finish(true); };   // same moment, without waiting for the close event
    ask.addEventListener('close', onClose);
    ask.addEventListener('click', onClick);
    ask.showModal();
  });

  // ---------------------------------------------------------- sidebar: fold to an icon rail
  const sidebar = $('.sidebar');
  const tipTargets = () => sidebar ? $$('.nav a, .sidebar > .btn, .sidebar > .search-commands, .sidebar-foot p, .sidebar-collapse', sidebar) : [];
  function updateTips() {
    if (!sidebar) return;
    const folded = document.documentElement.dataset.sidebar === 'collapsed';
    tipTargets().forEach(el => {
      const src = el.querySelector('.lbl');
      const text = (src || el.querySelector('span') || el).textContent.trim();
      if (folded) {
        el.dataset.tip = text;
        if (el.tagName !== 'P') { el.setAttribute('aria-label', text); el.dataset.ctAria = ''; }
      } else {
        delete el.dataset.tip;
        if ('ctAria' in el.dataset) { el.removeAttribute('aria-label'); delete el.dataset.ctAria; }
      }
    });
  }
  function setSidebar(folded, save) {
    const btn = $('.sidebar-collapse');
    if (folded) document.documentElement.dataset.sidebar = 'collapsed'; else delete document.documentElement.dataset.sidebar;
    if (save) store.set('ct-sidebar', folded ? 'collapsed' : 'open');
    if (btn) {
      btn.setAttribute('aria-expanded', !folded);
      $('.lbl', btn).textContent = folded ? 'Expand menu' : 'Collapse menu';
      $('use', btn).setAttribute('href', folded ? '#i-sidebar-unfold' : '#i-sidebar-fold');
    }
    updateTips();
  }
  if (sidebar) {
    // The labels are bare text next to an icon. Wrap them so CSS can fold them away and still leave them for screen readers.
    $$('.nav a, .sidebar > .btn, .sidebar-foot p', sidebar).forEach(el => {
      [...el.childNodes].forEach(n => {
        if (n.nodeType === 3 && n.textContent.trim()) {
          const span = document.createElement('span');
          span.className = 'lbl'; span.textContent = n.textContent.trim();
          if (/^Private mode:/.test(span.textContent)) span.dataset.privateText = '';
          n.replaceWith(span);
        }
      });
    });
    sidebar.insertAdjacentHTML('beforeend',
      '<button class="sidebar-collapse" type="button" aria-expanded="true"><svg class="icon" aria-hidden="true"><use href="#i-sidebar-fold"/></svg><span class="lbl">Collapse menu</span></button>');
    setSidebar(document.documentElement.dataset.sidebar === 'collapsed', false);
    document.addEventListener('click', e => {
      if (e.target.closest('.sidebar-collapse')) setSidebar(document.documentElement.dataset.sidebar !== 'collapsed', true);
    });
    document.addEventListener('keydown', e => {
      if ((e.ctrlKey || e.metaKey) && !e.altKey && !e.shiftKey && e.key.toLowerCase() === 'b' && !(e.target.closest && e.target.closest('[contenteditable]'))) {
        e.preventDefault(); setSidebar(document.documentElement.dataset.sidebar !== 'collapsed', true);
      }
    });
  }
  applyPrivate(isPrivate());

  // ---------------------------------------------------------- window tabs: Home, the open reviews, and +
  // The open reviews are prototype data in ct-tabs. Pages of a review select its tab; sidebar pages select Home.
  if (HAS_TABS) {
    const FLOW_AFTER_NEW = ['contract-check.html', 'privacy-check.html', 'running.html'];
    const REVIEW_PAGES = ['review.html', 'output.html'].concat(FLOW_AFTER_NEW);
    const DEFAULT_TABS = [{ id: 'brightline', title: 'Brightline web build', href: 'review.html' }];
    const readTabs = () => {
      try { const a = JSON.parse(store.get('ct-tabs')); if (Array.isArray(a)) return a.filter(t => t && t.id && t.title && t.href); } catch (_) {}
      return DEFAULT_TABS.slice();
    };
    let tabs = readTabs();
    let cur = null;
    if (PAGE === 'new-review.html') cur = { id: 'new', title: 'New review', href: 'new-review.html' };
    else if (REVIEW_PAGES.includes(PAGE)) cur = DEFAULT_TABS[0];
    if (cur) {
      if (FLOW_AFTER_NEW.includes(PAGE)) {   // the new review has become the named one: swap its tab
        const i = tabs.findIndex(t => t.id === 'new');
        if (i > -1) { if (tabs.some(t => t.id === cur.id)) tabs.splice(i, 1); else tabs[i] = cur; }
      }
      if (!tabs.some(t => t.id === cur.id)) tabs.push(cur);
      store.set('ct-tabs', JSON.stringify(tabs));
    }
    // Each review tab shows that review's checked share as a small pie (kept in ct-progress by id); a new review has none yet.
    const PIE_C = 21.99;
    const readProg = () => { try { return JSON.parse(store.get('ct-progress')) || {}; } catch (_) { return {}; } };
    const prog = readProg();
    if (!prog.brightline) prog.brightline = { checked: 2, total: 11 };
    const tabPie = id => {
      const p = prog[id];
      if (!p) return icon('doc');
      const off = (PIE_C * (1 - p.checked / p.total)).toFixed(2);
      return '<svg class="pie pie-tab' + (p.checked === p.total ? ' is-full' : '') + '" data-pie-id="' + id + '" viewBox="0 0 20 20" aria-hidden="true" focusable="false"><circle class="pie-ring" cx="10" cy="10" r="9"/><circle class="pie-fill" cx="10" cy="10" r="3.5" transform="rotate(-90 10 10)" style="stroke-dashoffset:' + off + '"/><circle class="pie-done" cx="10" cy="10" r="9.75"/><path class="pie-check" d="M6 10.4 8.6 12.9 14 7.4"/></svg>';
    };
    const icon = name => '<svg class="icon" aria-hidden="true"><use href="#i-' + name + '"/></svg>';
    document.body.insertAdjacentHTML('afterbegin', '<nav class="wintabs" aria-label="Open reviews"></nav>');
    const strip = $('.wintabs');
    const renderTabs = () => {
      strip.innerHTML = '<a class="wintab-home" href="home.html" aria-label="Home"' + (cur ? '' : ' aria-current="page"') + '>' + icon('home') + '</a>';
      tabs.forEach(t => {
        const on = !!cur && cur.id === t.id;
        const tab = document.createElement('div');
        tab.className = 'wintab' + (on ? ' is-current' : '');
        tab.innerHTML = '<a class="wintab-link" href="' + t.href + '"' + (on ? ' aria-current="page"' : '') + '>' + tabPie(t.id) + '<span class="wintab-title"></span></a>' +
          '<button class="wintab-close" type="button" data-tab="' + t.id + '">' + icon('x') + '</button>';
        $('.wintab-title', tab).textContent = t.title;
        $('.wintab-close', tab).setAttribute('aria-label', 'Close tab, ' + t.title);
        strip.appendChild(tab);
      });
      strip.insertAdjacentHTML('beforeend', '<a class="wintab-new" href="new-review.html" aria-label="New review">' + icon('plus') + '</a>');
    };
    renderTabs();
    document.addEventListener('ct-progress', e => {
      const d = e.detail || {};
      if (!d.id || !d.total) return;
      prog[d.id] = { checked: d.checked, total: d.total };
      if (!STATE) store.set('ct-progress', JSON.stringify(prog));   // a ?state= page is a still picture: it never changes the saved share
      $$('.wintab .pie[data-pie-id="' + d.id + '"]').forEach(p => {
        p.classList.toggle('is-still', !!d.still);
        $('.pie-fill', p).style.strokeDashoffset = (PIE_C * (1 - d.checked / d.total)).toFixed(2);
        p.classList.toggle('is-full', d.checked === d.total);
      });
    });
    strip.addEventListener('click', e => {
      const x = e.target.closest('.wintab-close');
      if (!x) return;
      tabs = tabs.filter(t => t.id !== x.dataset.tab);
      store.set('ct-tabs', JSON.stringify(tabs));
      if (cur && cur.id === x.dataset.tab) location.href = 'home.html'; else renderTabs();
    });
  }

  // ---------------------------------------------------------- flow stepper: it moves on every page of the flow
  // Only on pages with <ol class="steps" data-step="n">. On load the line into the current step draws in (step 1: its ring grows in).
  // Pressing the forward button marks this step done and starts the next line, then goes on 200 ms later. Reduced motion: no movement, no delay.
  const stepper = $('ol.steps[data-step]');
  if (stepper) {
    const calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
    try { sessionStorage.setItem('ct-step', stepper.dataset.step); } catch (e) {}
    if (!calm) {
      stepper.classList.add('is-arriving');
      void stepper.offsetWidth;   // flush the "before" look, then let the transitions run
      setTimeout(() => stepper.classList.remove('is-arriving'), 30);
      document.addEventListener('click', e => {
        const go = e.target.closest && e.target.closest('.flow-foot a.btn-primary[href]');
        const plain = e.button === 0 && !e.ctrlKey && !e.metaKey && !e.shiftKey && !e.altKey && !e.defaultPrevented;
        const href = go && go.getAttribute('href');
        const off = go && (go.getAttribute('aria-disabled') === 'true' || go.hasAttribute('disabled'));
        if (!go || !plain || off || !href || href.charAt(0) === '#' || go.target === '_blank' || stepper.classList.contains('is-leaving')) return;
        try {
          const cur = $('li[aria-current] .dot', stepper);
          if (cur && !cur.querySelector('.icon')) cur.insertAdjacentHTML('beforeend', '<svg class="icon"><use href="#i-check"/></svg>');
          e.preventDefault();
          stepper.classList.add('is-leaving');
          setTimeout(() => { location.href = go.href; }, 200);
        } catch (err) { /* navigate normally */ }
      });
    }
  }

  // ---------------------------------------------------------- the logo: the butterfly flicks its wings once
  // The logo file is one picture (butterfly, then the name), so it is shown twice, each copy cut to its own part:
  // .logo-fly shows the butterfly and .logo-name shows the name. Pointing at the logo, or reaching it with the keyboard,
  // folds the wings once (110 ms in, 180 ms out, styles.css). The files are unchanged. Reduced motion: no movement.
  const FLY = 256 / 1415;   // the butterfly's share of the logo's width
  $$('a.logo').forEach(link => {
    $$('img', link).forEach(img => {
      const pair = document.createElement('span'), fly = document.createElement('span'), name = document.createElement('span');
      pair.className = 'logo-pair ' + img.className; fly.className = 'logo-fly'; name.className = 'logo-name';
      const wing = img.cloneNode(); wing.className = ''; wing.alt = ''; wing.setAttribute('aria-hidden', 'true');
      img.replaceWith(pair); img.className = '';
      fly.append(wing); name.append(img); pair.append(fly, name);
    });
    link.style.setProperty('--fly', FLY);
  });
  if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {
    $$('a.logo, a.logo-symbol').forEach(link => {
      const flick = () => {
        if (link.classList.contains('is-flick')) return;
        link.classList.add('is-flick');
        setTimeout(() => link.classList.remove('is-flick'), 120);
      };
      link.addEventListener('pointerenter', flick);
      link.addEventListener('focus', flick);
    });
  }

  // open a dialog named in the URL hash (#detail-4) so pages can link straight to a state
  const h = location.hash.slice(1);
  const d = h && document.getElementById(h);
  if (d && d.tagName === 'DIALOG') d.showModal();
})();
