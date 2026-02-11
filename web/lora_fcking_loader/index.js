import { app } from "../../../scripts/app.js";

const MAX_LORAS = 5;

function isTarget(node) {
  return node?.comfyClass === "LoraFcKingLoader" || node?.type === "LoraFcKingLoader";
}

function getWidget(node, name) {
  return node?.widgets?.find((w) => w.name === name);
}

function setWidgetHidden(w, hidden) {
  if (!w) return;
  w.hidden = !!hidden;
  if (w.inputEl) w.inputEl.style.display = hidden ? "none" : "";
}

function buildSummary(node) {
  const countW = getWidget(node, "lora_count");
  const count = countW ? Number(countW.value || 1) : 1;
  const parts = [];

  for (let i = 1; i <= MAX_LORAS; i++) {
    if (i > count) break;
    const enabled = getWidget(node, `enabled_${i}`)?.value;
    const name = getWidget(node, `lora_name_${i}`)?.value || "None";
    const sm = getWidget(node, `strength_model_${i}`)?.value ?? 0;
    const sc = getWidget(node, `strength_clip_${i}`)?.value ?? 0;
    if (!enabled || name === "None") continue;
    parts.push(`#${i} ${name} (M:${Number(sm).toFixed(2)} C:${Number(sc).toFixed(2)})`);
  }

  return parts.length ? parts : ["no active loras"];
}

function applyDynamicUI(node) {
  const countW = getWidget(node, "lora_count");
  const count = countW ? Number(countW.value || 1) : 1;

  for (let i = 1; i <= MAX_LORAS; i++) {
    const hidden = i > count;
    setWidgetHidden(getWidget(node, `enabled_${i}`), hidden);
    setWidgetHidden(getWidget(node, `lora_name_${i}`), hidden);
    setWidgetHidden(getWidget(node, `strength_model_${i}`), hidden);
    setWidgetHidden(getWidget(node, `strength_clip_${i}`), hidden);
  }

  node.fckingSummary = buildSummary(node);
  if (node.computeSize) {
    const size = node.computeSize();
    if (size?.length === 2) {
      size[0] = Math.max(size[0], 360);
      size[1] = size[1] + 22;
      node.setSize(size);
    }
  }
  node.setDirtyCanvas(true, true);
}

function wrapWidgetCallbacks(node) {
  if (!node?.widgets) return;
  node.widgets.forEach((w) => {
    if (w.__fckWrapped) return;
    const orig = w.callback;
    w.callback = function () {
      const res = orig?.apply(this, arguments);
      applyDynamicUI(node);
      return res;
    };
    w.__fckWrapped = true;
  });
}

function styleNode(node) {
  node.bgcolor = "#0b0f14";
  node.color = "#ff6a00";
  node.title = "LoraFcKingLoader";
}

function elideText(ctx, text, maxWidth) {
  if (ctx.measureText(text).width <= maxWidth) return text;
  const ellipsis = "...";
  let t = text;
  while (t.length > 0 && ctx.measureText(t + ellipsis).width > maxWidth) {
    t = t.slice(0, -1);
  }
  return t.length ? t + ellipsis : ellipsis;
}

app.registerExtension({
  name: "lora.fcking.loader",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData?.name !== "LoraFcKingLoader") return;

    const origOnNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      origOnNodeCreated?.apply(this, arguments);
      styleNode(this);
      wrapWidgetCallbacks(this);
      applyDynamicUI(this);
    };

    const origOnConfigure = nodeType.prototype.onConfigure;
    nodeType.prototype.onConfigure = function () {
      const res = origOnConfigure?.apply(this, arguments);
      wrapWidgetCallbacks(this);
      applyDynamicUI(this);
      return res;
    };

    const origOnDrawForeground = nodeType.prototype.onDrawForeground;
    nodeType.prototype.onDrawForeground = function (ctx) {
      origOnDrawForeground?.apply(this, arguments);

      if (!isTarget(this)) return;

      const w = this.size[0];
      const h = this.size[1];
      const barH = 18;
      const y = h - barH - 4;
      const grad = ctx.createLinearGradient(0, y, w, y);
      grad.addColorStop(0, "#ff6a00");
      grad.addColorStop(1, "#ffd400");
      ctx.fillStyle = grad;
      ctx.fillRect(0, y, w, barH);

      ctx.fillStyle = "#0b0f14";
      ctx.font = "12px sans-serif";
      const label = (this.fckingSummary || ["no active loras"]).join(" | ");
      const maxText = w - 16;
      ctx.fillText(elideText(ctx, label, maxText), 8, y + 13);
    };
  },
});
