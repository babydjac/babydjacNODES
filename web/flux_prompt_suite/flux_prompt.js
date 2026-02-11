import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

class FluxNSFWPrompterUI {
  constructor(node) {
    this.node = node;
    this.node.properties = this.node.properties || {};
    this.controls = {};
    this._init();
  }

  _init() {
    const node = this.node;
    node.size = node.size || [360, 300];
    node.min_size = [340, 260];
    // Cache title bar height to align drawing and hit-testing with LiteGraph
    this.titleH = (typeof LiteGraph !== 'undefined' && LiteGraph.NODE_TITLE_HEIGHT) ? LiteGraph.NODE_TITLE_HEIGHT : 24;

    // Get widget refs
    const get = (n) => node.widgets?.find(w => w.name === n);
    this.wSubject = get('subject');
    this.wStyle = get('style');
    this.wCamera = get('camera');
    this.wLighting = get('lighting');
    this.wSpice = get('spice');
    this.wSafety = get('safety_level');
    this.wUseGrok = get('use_grok');
    this.wApiKey = get('grok_api_key');
    this.wGuidance = get('guidance_tags');
    this.wForbidden = get('forbidden_tags');
    this.wOverride = get('prompt_override');
    this.wCanvas = get('use_canvas_ui');

    // Hide or show depending on canvas toggle
    const hide = (w) => { if (!w) return; w.hidden = true; w.type = 'hidden'; w.computeSize = () => [0, -4]; };
    const show = (w) => { if (!w) return; w.hidden = false; if (w.type === 'hidden') w.type = 'text'; w.computeSize = null; };
    const canvasOn = !(this.wCanvas && this.wCanvas.value === false);
    if (canvasOn) {
      // Show core widgets and hide the rest for canvas UI
      [this.wSubject, this.wUseGrok, this.wApiKey, this.wCanvas].forEach(show);
      [this.wStyle, this.wCamera, this.wLighting, this.wSpice, this.wSafety, this.wGuidance, this.wForbidden, this.wOverride].forEach(hide);
    } else {
      // Native widgets only
      [this.wSubject, this.wUseGrok, this.wApiKey, this.wCanvas, this.wStyle, this.wCamera, this.wLighting, this.wSpice, this.wSafety, this.wGuidance, this.wForbidden, this.wOverride].forEach(show);
      // Add Generate/Copy buttons as native widgets if missing
      const hasGenerate = (node.widgets || []).some(w => w.name === 'Generate');
      if (!hasGenerate) node.addWidget('button', 'Generate', null, () => this.generate());
      const hasCopy = (node.widgets || []).some(w => w.name === 'Copy');
      if (!hasCopy) node.addWidget('button', 'Copy', null, () => {
        const text = (this.wOverride?.value || '').trim();
        try { navigator.clipboard.writeText(text); } catch {}
      });
    }

    // Default frontend values
    this.node.properties.subject = this.wSubject?.value || "portrait in studio";
    this.node.properties.spice = this.wSpice?.value ?? 0.35;

    node.onDrawForeground = (ctx) => {
      if (node.flags.collapsed) return;
      this.draw(ctx);
    };

    // Use the same handler signature Comfy nodes expect (e, pos, canvas)
    node.onMouseDown = (e, pos, canvas) => {
      if (this.wCanvas && this.wCanvas.value === false) return false;
      // Ignore header area (allows dragging node by title)
      if ((e.canvasY - node.pos[1]) < 0) return false;
      const handled = this.onMouseDown(e, pos, canvas);
      if (handled) app.graph.setDirtyCanvas(true);
      return handled;
    };
    node.onMouseMove = (e, pos, canvas) => {
      if (this.wCanvas && this.wCanvas.value === false) return false;
      // Always update hover cursor; handle drag when captured
      const hovered = this._hitTest(e);
      const c = app?.canvas?.canvas;
      if (c) c.style.cursor = hovered ? 'pointer' : '';
      if (!node.capture) return hovered ? true : false;
      const handled = this.onMouseMove(e, pos, canvas);
      if (handled) app.graph.setDirtyCanvas(true);
      return handled;
    };
    node.onMouseUp = (e) => {
      if (this.wCanvas && this.wCanvas.value === false) return false;
      if (!node.capture) return false;
      const handled = this.onMouseUp(e);
      if (handled) app.graph.setDirtyCanvas(true);
      return handled;
    };
  }

  draw(ctx) {
    // Respect toggle to disable canvas UI (use native widgets only)
    if (this.wCanvas && this.wCanvas.value === false) return;
    const pad = 10;
    const line = 26;
    let y = this.titleH + 6;
    // Respect toggle to disable canvas UI (use native widgets only)
    if (this.wCanvas && this.wCanvas.value === false) return;
    // Ensure font set before measuring chip widths
    ctx.font = "11px sans-serif";
    this.drawLabel(ctx, pad, y, "Flux NSFW Prompter");
    // Debug toggle button (top-right)
    const dbgW = 22; const dbgH = 18; const dbgX = this.node.size[0] - pad - dbgW; const dbgY = y - 14;
    this.controls.debugBtn = { x: dbgX, y: dbgY, w: dbgW, h: dbgH };
    ctx.fillStyle = this.node.properties.debug ? "#8a3" : "#444";
    ctx.strokeStyle = "#666"; ctx.beginPath(); ctx.roundRect(dbgX, dbgY, dbgW, dbgH, 4); ctx.fill(); ctx.stroke();
    ctx.fillStyle = "#eee"; ctx.font = "12px sans-serif"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.fillText("🐞", dbgX + dbgW/2, dbgY + dbgH/2 + 1);
    y += line;
    // Push custom UI precisely below native widgets (subject/use_grok/api_key)
    const visibleWidgets = (this.node.widgets || []).filter(w => !w.hidden);
    const defaultH = (typeof LiteGraph !== 'undefined' && LiteGraph.NODE_WIDGET_HEIGHT) ? LiteGraph.NODE_WIDGET_HEIGHT : 22;
    let widgetsHeight = 0;
    for (const w of visibleWidgets) {
      try {
        const sz = w.computeSize ? w.computeSize(this.node.size[0] - pad * 2) : [0, defaultH];
        const h = Array.isArray(sz) ? (sz[1] || defaultH) : defaultH;
        widgetsHeight += (h + 4);
      } catch { widgetsHeight += (defaultH + 4); }
    }
    y += widgetsHeight;

    // Style chips
    const chips = ["cinematic","glamour","artistic nude","editorial","photoreal"];
    y += this.drawChips(ctx, pad, y, chips, "style");

    // Camera / Lighting dropdown mocks (click cycles)
    y += 4;
    this.controls.camera = { x: pad, y, w: (this.node.size[0]-pad*3)/2, h: 24 };
    this.controls.lighting = { x: pad*2 + this.controls.camera.w, y, w: this.controls.camera.w, h: 24 };
    this.drawBox(ctx, this.controls.camera, `Camera: ${this.wCamera?.value || "50mm"}`);
    this.drawBox(ctx, this.controls.lighting, `Lighting: ${this.wLighting?.value || "softbox"}`);
    y += line + 2;

    // Spice slider (simple)
    this.controls.spice = { x: pad, y, w: this.node.size[0]-pad*2-60, h: 18 };
    this.drawSlider(ctx, this.controls.spice, this.node.properties.spice, 0, 1);
    this.drawText(ctx, this.controls.spice.x + this.controls.spice.w + 8, y+10, `spice ${(this.node.properties.spice).toFixed(2)}`);
    y += line + 6;

    // Generate + Copy buttons
    const w = (this.node.size[0]-pad*3)/2;
    this.controls.generate = { x: pad, y, w, h: 26 };
    this.controls.copy = { x: pad*2 + w, y, w, h: 26 };
    this.drawButton(ctx, this.controls.generate, "Generate");
    this.drawButton(ctx, this.controls.copy, "Copy");
    y += line + 2;

    // Preview box (prompt_override)
    this.controls.preview = { x: pad, y, w: this.node.size[0]-pad*2, h: Math.max(80, this.node.size[1]-y-10) };
    const prev = (this.wOverride?.value || "").trim();
    this.drawMultiline(ctx, this.controls.preview, prev || "Preview will appear here...");

    // Debug overlay for hitboxes
    if (this.node.properties.debug) {
      ctx.save();
      ctx.strokeStyle = "#f55"; ctx.lineWidth = 1; ctx.setLineDash([4,3]);
      for (const [key, r] of Object.entries(this.controls)) {
        if (!r) continue; ctx.strokeRect(r.x, r.y, r.w, r.h);
        ctx.fillStyle = "#faa"; ctx.font = "10px monospace"; ctx.textAlign = "left"; ctx.textBaseline = "top";
        ctx.fillText(key, r.x + 2, r.y + 2);
      }
      ctx.restore();
    }
  }

  // --- Drawing helpers ---
  drawLabel(ctx, x, y, text) { ctx.fillStyle = "#ccc"; ctx.font = "bold 12px sans-serif"; ctx.fillText(text, x, y); }
  drawText(ctx, x, y, text) { ctx.fillStyle = "#aaa"; ctx.font = "11px sans-serif"; ctx.fillText(text, x, y); }
  drawBox(ctx, r, text) {
    ctx.fillStyle = "#2b2b2b"; ctx.strokeStyle = "#444"; ctx.lineWidth = 1; ctx.beginPath(); ctx.roundRect(r.x, r.y, r.w, r.h, 4); ctx.fill(); ctx.stroke();
    ctx.fillStyle = "#ddd"; ctx.font = "11px monospace"; ctx.textBaseline = "middle"; ctx.fillText(text, r.x+8, r.y + r.h/2);
  }
  drawButton(ctx, r, label) {
    const grad = ctx.createLinearGradient(r.x, r.y, r.x, r.y + r.h);
    grad.addColorStop(0, "#5a5a5a"); grad.addColorStop(1, "#4a4a4a");
    ctx.fillStyle = grad; ctx.strokeStyle = "#666"; ctx.beginPath(); ctx.roundRect(r.x, r.y, r.w, r.h, 4); ctx.fill(); ctx.stroke();
    ctx.fillStyle = "#eee"; ctx.font = "12px sans-serif"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.fillText(label, r.x + r.w/2, r.y + r.h/2);
  }
  drawMultiline(ctx, r, text) {
    ctx.fillStyle = "#1f1f1f"; ctx.strokeStyle = "#444"; ctx.beginPath(); ctx.roundRect(r.x, r.y, r.w, r.h, 4); ctx.fill(); ctx.stroke();
    ctx.fillStyle = "#cfcfcf"; ctx.font = "11px monospace"; ctx.textAlign = "left"; ctx.textBaseline = "top";
    const lines = this.wrapText(ctx, text, r.w-12);
    let y = r.y + 6; lines.forEach(line => { ctx.fillText(line, r.x+6, y); y += 14; });
  }
  drawSlider(ctx, r, value, min, max) {
    ctx.fillStyle = "#3a3a3a"; ctx.fillRect(r.x, r.y+6, r.w, 4);
    const t = (value - min) / (max - min);
    const x = r.x + Math.max(0, Math.min(1, t)) * r.w;
    ctx.fillStyle = "#88c"; ctx.beginPath(); ctx.arc(x, r.y+8, 6, 0, Math.PI*2); ctx.fill();
  }
  drawChips(ctx, x, y, arr, key) {
    let cx = x, h = 0;
    const padH = 8, padV = 4;
    arr.forEach(label => {
      const text = `${label}`; const w = ctx.measureText ? (ctx.measureText(text).width + padH*2) : (text.length*6 + padH*2);
      const r = { x: cx, y, w, h: 22 };
      this.controls[`chip_${key}_${label}`] = r;
      ctx.fillStyle = (this.wStyle?.value === label) ? "#466" : "#2d2d2d";
      ctx.strokeStyle = "#555"; ctx.beginPath(); ctx.roundRect(r.x, r.y, r.w, r.h, 10); ctx.fill(); ctx.stroke();
      ctx.fillStyle = "#ddd"; ctx.font = "11px sans-serif"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
      ctx.fillText(text, r.x + r.w/2, r.y + r.h/2);
      cx += w + 6; h = Math.max(h, r.h);
    });
    return h + 6;
  }
  wrapText(ctx, text, maxWidth) {
    const words = (text||"").split(/\s+/); const lines = []; let cur = "";
    words.forEach(w => { const test = cur ? `${cur} ${w}` : w; if (ctx.measureText(test).width > maxWidth) { if (cur) lines.push(cur); cur = w; } else { cur = test; } });
    if (cur) lines.push(cur); return lines;
  }

  // --- Interaction ---
  onMouseDown(e) {
    const x = e.canvasX - this.node.pos[0];
    const y = e.canvasY - this.node.pos[1];
    // Let header + widget area be draggable to move the node / native widgets handle their own
    let widgetsHeight = 0;
    const visibleWidgets = (this.node.widgets || []).filter(w => !w.hidden);
    const defaultH = (typeof LiteGraph !== 'undefined' && LiteGraph.NODE_WIDGET_HEIGHT) ? LiteGraph.NODE_WIDGET_HEIGHT : 22;
    for (const w of visibleWidgets) {
      try {
        const sz = w.computeSize ? w.computeSize(this.node.size[0] - 20) : [0, defaultH];
        widgetsHeight += ((Array.isArray(sz) ? (sz[1] || defaultH) : defaultH) + 4);
      } catch { widgetsHeight += (defaultH + 4); }
    }
    if (y < this.titleH + widgetsHeight) return false;
    for (const [key, r] of Object.entries(this.controls)) {
      if (x >= r.x && x <= r.x+r.w && y >= r.y && y <= r.y+r.h) {
        // Immediate actions for buttons/chips/boxes; capture only for sliders
        if (key === 'debugBtn') { this.node.properties.debug = !this.node.properties.debug; return true; }
        if (key === 'spice') {
          this.node.capture = key; this.node.captureInput?.(true);
          return true;
        }
        this._triggerControl(key);
        return true;
      }
    }
    return false;
  }
  onMouseMove(e) {
    if (!this.node.capture) return false;
    if (this.node.capture === "spice") {
      const r = this.controls.spice; const t = Math.max(0, Math.min(1, (e.canvasX - this.node.pos[0] - r.x)/r.w));
      const v = +(t.toFixed(2)); this.node.properties.spice = v; if (this.wSpice) this.wSpice.value = v; app.graph.setDirtyCanvas(true);
      return true;
    }
    return false;
  }
  onMouseUp(e) {
    if (!this.node.capture) return false;
    const key = this.node.capture; this.node.capture = false; this.node.captureInput?.(false);
    const x = e.canvasX - this.node.pos[0]; const y = e.canvasY - this.node.pos[1];
    const r = this.controls[key];
    if (r && x >= r.x && x <= r.x+r.w && y >= r.y && y <= r.y+r.h) {
      // Slider was captured; other controls already handled on mousedown
      if (key === 'spice') { /* finalize already updated */ }
    }
    return true;
  }

  _hitTest(e) {
    const x = e.canvasX - this.node.pos[0];
    const y = e.canvasY - this.node.pos[1];
    for (const r of Object.values(this.controls)) {
      if (x >= r.x && x <= r.x+r.w && y >= r.y && y <= r.y+r.h) return true;
    }
    return false;
  }

  _triggerControl(key) {
    if (key.startsWith("chip_style_")) {
      const val = key.replace("chip_style_", "").trim(); if (this.wStyle) this.wStyle.value = val; app.graph.setDirtyCanvas(true); return;
    }
    if (key === "camera") {
      const order = ["35mm","50mm","85mm","macro","telephoto"]; const cur = this.wCamera?.value || order[1];
      const next = order[(order.indexOf(cur)+1) % order.length]; if (this.wCamera) this.wCamera.value = next; app.graph.setDirtyCanvas(true); return;
    }
    if (key === "lighting") {
      const order = ["softbox","rembrandt","split","rim","golden hour","hdr studio"]; const cur = this.wLighting?.value || order[0];
      const next = order[(order.indexOf(cur)+1) % order.length]; if (this.wLighting) this.wLighting.value = next; app.graph.setDirtyCanvas(true); return;
    }
    if (key === "generate") { this.generate(); return; }
    if (key === "copy") { const text = (this.wOverride?.value || "").trim(); try { navigator.clipboard.writeText(text); } catch {} return; }
  }

  async generate() {
    // Compose params and hit the optional route; if not configured, server returns local template
    const body = {
      subject: this.wSubject?.value || this.node.properties.subject || "subject",
      style: this.wStyle?.value || "cinematic",
      camera: this.wCamera?.value || "50mm",
      lighting: this.wLighting?.value || "softbox",
      spice: this.node.properties.spice ?? this.wSpice?.value ?? 0.35,
      safety_level: this.wSafety?.value || "standard",
      use_grok: !!(this.wUseGrok?.value),
      api_key: (this.wApiKey?.value || "").trim(),
      guidance_tags: this.wGuidance?.value || "",
      forbidden_tags: this.wForbidden?.value || "",
      temperature: 0.5,
      max_tokens: 128,
      grok_model: "grok-2-latest",
    };
    try {
      const res = await api.fetchApi("/flux_nsfw_prompter/generate", { method: "POST", body: JSON.stringify(body) });
      const json = await res.json();
      if (json?.ok) {
        if (this.wOverride) this.wOverride.value = json.prompt;
        app.graph.setDirtyCanvas(true);
      } else {
        console.warn("FluxNSFWPrompter: generation failed", json);
      }
    } catch (err) {
      console.error("FluxNSFWPrompter: route error", err);
    }
  }
}

app.registerExtension({
  name: "FluxNSFWPrompter.UI",
  beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== "FluxNSFWPrompter") return;
    const old = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function() {
      old?.apply(this, arguments);
      this._flux_ui = new FluxNSFWPrompterUI(this);
    };
  }
});
