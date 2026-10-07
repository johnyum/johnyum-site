// minimal stand-in for the design canvas runtime: renderVals + {{}} + sc-for + sc-if
window.DCLogic = class { constructor(){ this.props = {}; } };
document.addEventListener('DOMContentLoaded', () => {
  const src = document.querySelector('script[data-dc-script]').textContent;
  const C = new Function(src + '; return Component;')();
  const vals = new C().renderVals();
  const root = document.querySelector('x-dc');
  root.querySelectorAll('helmet').forEach(h => { document.head.append(...h.childNodes); h.remove(); });
  const get = (path, scope) => path.split('.').reduce((o, k) => o == null ? o : o[k], scope);
  const fill = (s, scope) => s.replace(/\{\{([^}]+)\}\}/g, (_, p) => { const v = get(p.trim(), scope); return v == null ? '' : v; });
  function walk(node, scope) {
    for (const el of [...node.children]) {
      if (el.tagName === 'SC-FOR') {
        const list = get(el.getAttribute('list').replace(/[{}]/g, '').trim(), scope) || [];
        const as = el.getAttribute('as'); const tpl = el.innerHTML; const frag = document.createElement('div');
        list.forEach(item => { const d = document.createElement('div'); d.innerHTML = tpl; walk(d, { ...scope, [as]: item }); frag.append(...d.childNodes); });
        el.replaceWith(...frag.childNodes); continue;
      }
      if (el.tagName === 'SC-IF') {
        const v = get(el.getAttribute('value').replace(/[{}]/g, '').trim(), scope);
        if (!v) { el.remove(); continue; } walk(el, scope); el.replaceWith(...el.childNodes); continue;
      }
      for (const a of [...el.attributes]) a.value = fill(a.value, scope);
      for (const t of [...el.childNodes]) if (t.nodeType === 3) t.textContent = fill(t.textContent, scope);
      walk(el, scope);
    }
  }
  walk(root, vals);
});
