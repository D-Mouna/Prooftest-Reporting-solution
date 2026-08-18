/**
 * Resolve asset and API paths for both:
 *   - file:///.../static/index.html  (preview / offline)
 *   - http://127.0.0.1:8080/         (live service; <base href="/static/"> injected)
 */
(function () {
  const isFile = window.location.protocol === "file:";
  const baseEl = document.querySelector("base[href]");
  const baseHref = baseEl ? baseEl.getAttribute("href").replace(/\/?$/, "/") : "";

  function join(base, path) {
    return (base + path).replace(/([^:]\/)\/+/g, "$1");
  }

  window.UI = {
    isFile,
    isLive: !isFile,
    asset(path) {
      const clean = path.replace(/^\//, "");
      if (isFile) return clean;
      if (baseHref) return join(baseHref, clean);
      return join("/static/", clean);
    },
    api(path) {
      const clean = path.startsWith("/") ? path : `/${path}`;
      if (isFile) return null;
      return clean;
    },
  };
})();
