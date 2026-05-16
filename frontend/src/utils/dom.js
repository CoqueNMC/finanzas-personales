/**
 * Helpers de DOM para reducir boilerplate (DRY).
 */

export const $ = (selector, parent = document) => parent.querySelector(selector);
export const $$ = (selector, parent = document) => [...parent.querySelectorAll(selector)];
export const el = (tag, attrs = {}, ...children) => {
  const e = document.createElement(tag);
  Object.entries(attrs).forEach(([k, v]) => {
    if (k === "class") e.className = v;
    else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
    else e.setAttribute(k, v);
  });
  children.forEach((c) => e.append(typeof c === "string" ? document.createTextNode(c) : c));
  return e;
};

export const setHtml = (selector, html) => {
  const node = $(selector);
  if (node) node.innerHTML = html;
};

export const show = (selector) => $(selector)?.classList.remove("hidden");
export const hide = (selector) => $(selector)?.classList.add("hidden");
