from __future__ import annotations

from pathlib import Path

from jinja2 import Template

WORKBENCH_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dental DICOM Local Workbench</title>
  <style>
    :root {
      color-scheme: light;
      --ink: #18212f;
      --muted: #5f6b7a;
      --line: #d9e0e8;
      --soft: #f5f7fa;
      --accent: #0f766e;
      --accent-dark: #0b534d;
      --danger: #b42318;
      --warn-bg: #fff7df;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: #ffffff;
      letter-spacing: 0;
    }
    header {
      padding: 28px clamp(18px, 4vw, 48px) 20px;
      border-bottom: 1px solid var(--line);
      background: linear-gradient(180deg, #ffffff 0%, #f9fbfc 100%);
    }
    h1 {
      margin: 0 0 8px;
      font-size: clamp(1.55rem, 2.5vw, 2.2rem);
      line-height: 1.15;
      letter-spacing: 0;
    }
    h2 {
      margin: 0 0 14px;
      font-size: 1.05rem;
      letter-spacing: 0;
    }
    p { margin: 0; color: var(--muted); line-height: 1.5; }
    main {
      display: grid;
      grid-template-columns: minmax(260px, 360px) minmax(0, 1fr);
      gap: 24px;
      padding: 24px clamp(18px, 4vw, 48px) 42px;
    }
    section {
      min-width: 0;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      background: #ffffff;
    }
    .stack { display: grid; gap: 14px; }
    .wide { display: grid; gap: 18px; }
    .warning {
      background: var(--warn-bg);
      border: 1px solid #f5d06f;
      border-radius: 8px;
      padding: 12px;
      color: #59410b;
    }
    label {
      display: grid;
      gap: 6px;
      font-size: 0.86rem;
      color: var(--muted);
    }
    input, select, textarea {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 9px 10px;
      font: inherit;
      color: var(--ink);
      background: #fff;
      min-height: 40px;
    }
    textarea {
      min-height: 180px;
      resize: vertical;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 0.85rem;
      line-height: 1.45;
    }
    button {
      border: 0;
      border-radius: 6px;
      padding: 10px 12px;
      min-height: 40px;
      font: inherit;
      font-weight: 700;
      color: #fff;
      background: var(--accent);
      cursor: pointer;
    }
    button:hover { background: var(--accent-dark); }
    button.secondary {
      background: #324154;
    }
    button.secondary:hover {
      background: #1f2937;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }
    .actions {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
    }
    .status {
      min-height: 28px;
      padding: 8px 10px;
      border-radius: 6px;
      background: var(--soft);
      color: var(--muted);
      font-size: 0.9rem;
    }
    .status.ok { color: #135e3b; background: #e9f8ef; }
    .status.fail { color: var(--danger); background: #fff0ee; }
    .preview {
      display: grid;
      gap: 10px;
    }
    .preview img {
      width: min(100%, 260px);
      aspect-ratio: 1;
      object-fit: contain;
      image-rendering: pixelated;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--soft);
    }
    .links {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }
    a {
      color: #0b63ce;
      text-decoration: none;
      font-weight: 600;
    }
    a:hover { text-decoration: underline; }
    code {
      background: var(--soft);
      border: 1px solid var(--line);
      border-radius: 4px;
      padding: 1px 4px;
    }
    @media (max-width: 860px) {
      main { grid-template-columns: 1fr; }
      .grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <header>
    <h1>Dental DICOM Local Workbench | 牙科 DICOM 本地工作台</h1>
    <p>
      Local synthetic-data workflow UI for inspection, anonymization, validation,
      previews, and demo evidence.
    </p>
  </header>
  <main>
    <aside class="stack">
      <section class="stack">
        <h2>Safety Boundary</h2>
        <p class="warning">
          Use synthetic or explicitly approved test DICOM files only. Keep real patient
          data outside this local API root.
        </p>
        <p>API root: <code>{{ root_dir }}</code></p>
        <div class="links">
          <a href="/docs">API docs</a>
          <a href="/">API JSON</a>
        </div>
      </section>
      <section class="stack">
        <h2>Run Demo</h2>
        <label>Output directory
          <input id="demo-output" value="workbench-demo">
        </label>
        <label>Profile
          <select id="demo-profile">
            {% for profile in profiles %}
            <option value="{{ profile }}">{{ profile }}</option>
            {% endfor %}
          </select>
        </label>
        <button id="run-demo">Run Synthetic Demo</button>
        <p>Open <code>workbench-demo/reports/demo-summary.html</code> after the run.</p>
      </section>
    </aside>
    <div class="wide">
      <section class="stack">
        <h2>Core Workflow</h2>
        <div class="grid">
          <label>Input DICOM
            <input id="input-path" value="input/sample.synthetic.dcm">
          </label>
          <label>Output DICOM
            <input id="output-path" value="outputs/sample.workbench.dcm">
          </label>
          <label>Input directory
            <input id="input-dir" value="input">
          </label>
          <label>Preview PNG
            <input id="preview-path" value="reports/workbench-preview.png">
          </label>
          <label>Profile
            <select id="profile">
              {% for profile in profiles %}
              <option value="{{ profile }}">{{ profile }}</option>
              {% endfor %}
            </select>
          </label>
        </div>
        <div class="actions">
          <button id="health" class="secondary">Health</button>
          <button id="inventory">Inventory</button>
          <button id="inspect">Inspect</button>
          <button id="anonymize">Anonymize</button>
          <button id="validate">Validate</button>
          <button id="preview">Preview</button>
        </div>
        <div id="status" class="status">Ready.</div>
      </section>
      <section class="grid">
        <div class="stack">
          <h2>JSON Result</h2>
          <textarea id="result" readonly>{}</textarea>
        </div>
        <div class="preview">
          <h2>Preview</h2>
          <img id="preview-image" alt="Generated DICOM preview" hidden>
          <p id="preview-note">Run Preview after creating or selecting a DICOM file.</p>
        </div>
      </section>
    </div>
  </main>
  <script>
    const statusEl = document.getElementById("status");
    const resultEl = document.getElementById("result");
    const imageEl = document.getElementById("preview-image");
    const noteEl = document.getElementById("preview-note");

    function value(id) {
      return document.getElementById(id).value.trim();
    }

    function showStatus(message, ok = true) {
      statusEl.textContent = message;
      statusEl.className = ok ? "status ok" : "status fail";
    }

    function showResult(data) {
      resultEl.value = JSON.stringify(data, null, 2);
    }

    async function callJson(path, payload = null) {
      const options = payload
        ? {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload)
          }
        : {};
      const response = await fetch(path, options);
      const text = await response.text();
      let data;
      try {
        data = text ? JSON.parse(text) : {};
      } catch {
        data = {raw: text};
      }
      if (!response.ok) {
        throw new Error(data.detail || response.statusText);
      }
      return data;
    }

    async function run(label, path, payload = null) {
      showStatus(`${label} running...`);
      try {
        const data = await callJson(path, payload);
        showResult(data);
        showStatus(`${label} complete.`);
        return data;
      } catch (error) {
        showResult({error: String(error.message || error)});
        showStatus(`${label} failed.`, false);
        return null;
      }
    }

    document.getElementById("health").addEventListener("click", () => {
      run("Health", "/health");
    });
    document.getElementById("inventory").addEventListener("click", () => {
      run("Inventory", "/inventory", {path: value("input-dir")});
    });
    document.getElementById("inspect").addEventListener("click", () => {
      run("Inspect", "/inspect", {path: value("input-path")});
    });
    document.getElementById("anonymize").addEventListener("click", () => {
      run("Anonymize", "/anonymize", {
        input_path: value("input-path"),
        output_path: value("output-path"),
        profile: value("profile")
      });
    });
    document.getElementById("validate").addEventListener("click", () => {
      run("Validate", "/validate", {path: value("output-path")});
    });
    document.getElementById("preview").addEventListener("click", async () => {
      const data = await run("Preview", "/preview", {
        input_path: value("output-path") || value("input-path"),
        output_path: value("preview-path"),
        max_size: 512
      });
      if (data) {
        const encodedPath = encodeURIComponent(value("preview-path")).replaceAll("%2F", "/");
        const imageUrl = `/files/${encodedPath}?v=${Date.now()}`;
        imageEl.src = imageUrl;
        imageEl.hidden = false;
        noteEl.textContent = value("preview-path");
      }
    });
    document.getElementById("run-demo").addEventListener("click", () => {
      run("Synthetic demo", "/demo", {
        output_dir: value("demo-output"),
        profile: value("demo-profile"),
        rect: "1,0,1,1"
      });
    });
  </script>
</body>
</html>
"""
)


def render_workbench_html(root_dir: Path, profiles: list[str]) -> str:
    return WORKBENCH_TEMPLATE.render(root_dir=str(root_dir), profiles=profiles)
