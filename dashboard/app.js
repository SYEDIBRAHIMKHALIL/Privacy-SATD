const DATA_BASE = "../data/results";
const REPORT_URL = `${DATA_BASE}/report.json`;
const EXAMPLES_URL = `${DATA_BASE}/examples.json`;

const setText = (id, value) => {
  const el = document.getElementById(id);
  if (el) {
    el.textContent = value;
  }
};

const escapeHtml = (value) => {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
};

const renderBars = (containerId, items) => {
  const container = document.getElementById(containerId);
  if (!container) {
    return;
  }
  container.innerHTML = "";
  if (!items || items.length === 0) {
    container.innerHTML = '<div class="muted">No data.</div>';
    return;
  }
  const maxValue = Math.max(...items.map((item) => item.count), 1);
  items.forEach((item) => {
    const row = document.createElement("div");
    row.className = "bar-row";
    const width = Math.max((item.count / maxValue) * 100, 4);
    row.innerHTML = `
      <div class="bar-label" title="${escapeHtml(item.label)}">${escapeHtml(item.label)}</div>
      <div class="bar-track"><div class="bar-fill" style="width: ${width.toFixed(1)}%"></div></div>
      <div class="bar-count">${item.count}</div>
    `;
    container.appendChild(row);
  });
};

const renderExamples = (items) => {
  const container = document.getElementById("examplesList");
  if (!container) {
    return;
  }
  container.innerHTML = "";
  if (!items || items.length === 0) {
    container.innerHTML = '<div class="muted">No examples available.</div>';
    return;
  }
  items.slice(0, 6).forEach((item) => {
    const card = document.createElement("div");
    card.className = "example";
    const meta = `${escapeHtml(item.repo || "")}` +
      (item.source_type ? ` | ${escapeHtml(item.source_type)}` : "");
    card.innerHTML = `
      <div class="example-meta">${meta}</div>
      <div class="example-text">${escapeHtml(item.text || "")}</div>
    `;
    container.appendChild(card);
  });
};

const formatDate = (isoValue) => {
  if (!isoValue) {
    return "-";
  }
  const date = new Date(isoValue);
  if (Number.isNaN(date.valueOf())) {
    return isoValue;
  }
  return date.toLocaleString();
};

const loadJson = async (url) => {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Failed to load ${url}`);
  }
  return response.json();
};

const init = async () => {
  try {
    const report = await loadJson(REPORT_URL);
    setText("generatedAt", formatDate(report.generated_at));
    setText("totalInstances", report.total_instances ?? "-");
    setText("uniqueRepos", report.unique_repos ?? "-");

    renderBars("chartRepos", report.top_repos || []);
    renderBars("chartKeywords", report.top_keywords || []);
    renderBars("chartSources", report.source_counts || []);
    renderBars("chartGdpr", report.gdpr_counts || []);

    const examples = await loadJson(EXAMPLES_URL);
    renderExamples(examples);
  } catch (error) {
    console.error(error);
    const container = document.getElementById("examplesList");
    if (container) {
      container.innerHTML = '<div class="muted">Unable to load report data.</div>';
    }
  }
};

init();
