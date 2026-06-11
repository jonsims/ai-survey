// Emma's Estates — tab switching + listings grid population
(function () {
  'use strict';

  // ---- Tab switching ---------------------------------------------
  const tabs = document.querySelectorAll('.tab');
  const views = document.querySelectorAll('.view');

  function activate(name) {
    tabs.forEach(t => t.classList.toggle('is-active', t.dataset.tab === name));
    views.forEach(v => v.classList.toggle('is-active', v.dataset.view === name));
  }

  tabs.forEach(t => {
    t.addEventListener('click', () => activate(t.dataset.tab));
  });

  document.querySelectorAll('[data-tab-link]').forEach(a => {
    a.addEventListener('click', (e) => {
      e.preventDefault();
      activate(a.dataset.tabLink);
    });
  });

  // ---- Build listings grid ---------------------------------------
  const grid = document.querySelector('.listings-grid');
  if (grid) {
    const tones = ['forest', 'brass', 'slate', 'forest', 'slate', 'brass', 'forest', 'brass'];
    const data = [
      { addr: '412 Linden Walk',        sub: 'Brookline · Single-family',     bd: '5 bd', ba: '4.5 ba', sf: '4,820 sqft', tag: 'Exclusive',   price: '3.85', note: '3 offers' },
      { addr: '7 Acorn Hollow Rd',      sub: 'Weston · Estate',                bd: '6 bd', ba: '5 ba',   sf: '6,100 sqft', tag: 'Open Sun.',   price: '5.95', note: 'Just listed' },
      { addr: '88 Beacon Hill Pl, #4',  sub: 'Boston · Condominium',           bd: '3 bd', ba: '3 ba',   sf: '2,640 sqft', tag: 'Coming',      price: '2.40', note: 'Photos Thu' },
      { addr: '14 Hawthorn Rd',         sub: 'Newton · Single-family',         bd: '4 bd', ba: '3 ba',   sf: '3,210 sqft', tag: 'In escrow',   price: '2.65', note: 'Closes Fri' },
      { addr: '31 Cobblers Ln',         sub: 'Lexington · Single-family',      bd: '4 bd', ba: '2.5 ba', sf: '2,980 sqft', tag: 'Reduced',     price: '1.69', note: '↓ from $1.78M' },
      { addr: '19 Fairway Cir',         sub: 'Wellesley · Single-family',      bd: '5 bd', ba: '4 ba',   sf: '3,840 sqft', tag: 'Pending',     price: '2.10', note: 'Closes Thu' },
      { addr: '6 Mill Pond Rd',         sub: 'Concord · Single-family',        bd: '4 bd', ba: '3 ba',   sf: '2,720 sqft', tag: 'Pending',     price: '1.78', note: 'Closes Tue' },
      { addr: '221 Marlborough St',     sub: 'Back Bay · Brownstone',          bd: '4 bd', ba: '3.5 ba', sf: '3,580 sqft', tag: 'Open Sat.',   price: '4.95', note: 'Just listed' },
    ];
    const svgFor = (tone) => {
      const variants = [
        // pitched roof + side wing
        '<path d="M20 80 L20 50 L55 28 L90 50 L90 80 Z" fill="currentColor" opacity=".55"/><path d="M90 80 L90 58 L120 42 L150 58 L150 80 Z" fill="currentColor" opacity=".78"/><rect x="46" y="58" width="10" height="22" fill="#FAF7F0"/><rect x="32" y="56" width="8" height="8" fill="#FAF7F0" opacity=".9"/><rect x="68" y="56" width="8" height="8" fill="#FAF7F0" opacity=".9"/><rect x="110" y="62" width="6" height="18" fill="#FAF7F0"/><rect x="126" y="60" width="6" height="6" fill="#FAF7F0" opacity=".9"/>',
        // colonial
        '<rect x="30" y="40" width="100" height="40" fill="currentColor" opacity=".72"/><path d="M30 40 L80 22 L130 40 Z" fill="currentColor" opacity=".55"/><rect x="44" y="52" width="10" height="14" fill="#FAF7F0"/><rect x="64" y="52" width="10" height="14" fill="#FAF7F0"/><rect x="84" y="52" width="10" height="14" fill="#FAF7F0"/><rect x="104" y="52" width="10" height="14" fill="#FAF7F0"/><rect x="74" y="66" width="12" height="14" fill="#FAF7F0" opacity=".75"/>',
        // estate w/ wings
        '<path d="M14 80 L14 46 L34 46 L34 30 L100 30 L100 46 L146 46 L146 80 Z" fill="currentColor" opacity=".68"/><rect x="44" y="42" width="14" height="14" fill="#FAF7F0"/><rect x="64" y="42" width="14" height="14" fill="#FAF7F0"/><rect x="84" y="42" width="14" height="14" fill="#FAF7F0"/><rect x="108" y="58" width="10" height="22" fill="#FAF7F0"/><rect x="124" y="58" width="10" height="10" fill="#FAF7F0" opacity=".9"/><rect x="22" y="58" width="10" height="10" fill="#FAF7F0" opacity=".9"/>',
        // brownstone row
        '<rect x="14" y="38" width="32" height="42" fill="currentColor" opacity=".7"/><rect x="48" y="34" width="32" height="46" fill="currentColor" opacity=".58"/><rect x="82" y="40" width="32" height="40" fill="currentColor" opacity=".75"/><rect x="116" y="36" width="32" height="44" fill="currentColor" opacity=".62"/><rect x="22" y="50" width="6" height="10" fill="#FAF7F0"/><rect x="32" y="50" width="6" height="10" fill="#FAF7F0"/><rect x="56" y="46" width="6" height="10" fill="#FAF7F0"/><rect x="66" y="46" width="6" height="10" fill="#FAF7F0"/><rect x="90" y="52" width="6" height="10" fill="#FAF7F0"/><rect x="100" y="52" width="6" height="10" fill="#FAF7F0"/><rect x="124" y="48" width="6" height="10" fill="#FAF7F0"/><rect x="134" y="48" width="6" height="10" fill="#FAF7F0"/><rect x="26" y="66" width="8" height="14" fill="#FAF7F0" opacity=".9"/><rect x="60" y="62" width="8" height="18" fill="#FAF7F0" opacity=".9"/><rect x="94" y="66" width="8" height="14" fill="#FAF7F0" opacity=".9"/><rect x="128" y="64" width="8" height="16" fill="#FAF7F0" opacity=".9"/>',
      ];
      const idx = Math.abs(tone.charCodeAt(0)) % variants.length;
      return variants[idx];
    };

    grid.innerHTML = data.map((d, i) => {
      const tone = tones[i % tones.length];
      // pick svg based on index for variety
      const variantIdx = i % 4;
      const variants = [
        // pitched
        '<path d="M20 80 L20 50 L55 28 L90 50 L90 80 Z" fill="currentColor" opacity=".55"/><path d="M90 80 L90 58 L120 42 L150 58 L150 80 Z" fill="currentColor" opacity=".78"/><rect x="46" y="58" width="10" height="22" fill="#FAF7F0"/><rect x="32" y="56" width="8" height="8" fill="#FAF7F0" opacity=".9"/><rect x="68" y="56" width="8" height="8" fill="#FAF7F0" opacity=".9"/><rect x="110" y="62" width="6" height="18" fill="#FAF7F0"/><rect x="126" y="60" width="6" height="6" fill="#FAF7F0" opacity=".9"/>',
        // colonial
        '<rect x="30" y="40" width="100" height="40" fill="currentColor" opacity=".72"/><path d="M30 40 L80 22 L130 40 Z" fill="currentColor" opacity=".55"/><rect x="44" y="52" width="10" height="14" fill="#FAF7F0"/><rect x="64" y="52" width="10" height="14" fill="#FAF7F0"/><rect x="84" y="52" width="10" height="14" fill="#FAF7F0"/><rect x="104" y="52" width="10" height="14" fill="#FAF7F0"/><rect x="74" y="66" width="12" height="14" fill="#FAF7F0" opacity=".75"/>',
        // estate
        '<path d="M14 80 L14 46 L34 46 L34 30 L100 30 L100 46 L146 46 L146 80 Z" fill="currentColor" opacity=".68"/><rect x="44" y="42" width="14" height="14" fill="#FAF7F0"/><rect x="64" y="42" width="14" height="14" fill="#FAF7F0"/><rect x="84" y="42" width="14" height="14" fill="#FAF7F0"/><rect x="108" y="58" width="10" height="22" fill="#FAF7F0"/><rect x="124" y="58" width="10" height="10" fill="#FAF7F0" opacity=".9"/><rect x="22" y="58" width="10" height="10" fill="#FAF7F0" opacity=".9"/>',
        // brownstone
        '<rect x="14" y="38" width="32" height="42" fill="currentColor" opacity=".7"/><rect x="48" y="34" width="32" height="46" fill="currentColor" opacity=".58"/><rect x="82" y="40" width="32" height="40" fill="currentColor" opacity=".75"/><rect x="116" y="36" width="32" height="44" fill="currentColor" opacity=".62"/><rect x="22" y="50" width="6" height="10" fill="#FAF7F0"/><rect x="32" y="50" width="6" height="10" fill="#FAF7F0"/><rect x="56" y="46" width="6" height="10" fill="#FAF7F0"/><rect x="66" y="46" width="6" height="10" fill="#FAF7F0"/><rect x="90" y="52" width="6" height="10" fill="#FAF7F0"/><rect x="100" y="52" width="6" height="10" fill="#FAF7F0"/><rect x="124" y="48" width="6" height="10" fill="#FAF7F0"/><rect x="134" y="48" width="6" height="10" fill="#FAF7F0"/>',
      ];
      const inner = variants[variantIdx];
      return `
        <article class="lcard">
          <div class="listing-img" data-tone="${tone}">
            <svg viewBox="0 0 160 110" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
              <rect width="160" height="110" fill="currentColor" opacity=".14"/>
              ${inner}
              <path d="M0 80 L160 80 L160 110 L0 110 Z" fill="#000" opacity=".06"/>
            </svg>
            <span class="listing-tag">${d.tag}</span>
          </div>
          <div class="lcard-body">
            <div>
              <p class="listing-addr">${d.addr}</p>
              <p class="listing-sub">${d.sub}</p>
              <ul class="listing-meta"><li>${d.bd}</li><li>${d.ba}</li><li>${d.sf}</li></ul>
            </div>
            <div class="listing-price">
              <p class="price">$${d.price}<span>M</span></p>
              <p class="price-sub">${d.note}</p>
            </div>
          </div>
        </article>`;
    }).join('');
  }
})();
