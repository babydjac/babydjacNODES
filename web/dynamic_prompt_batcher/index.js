import { app } from "../../../scripts/app.js";

app.registerExtension({
  name: "babydjac.dynamic_prompt_batcher",

  async nodeCreated(node) {
    if (node.comfyClass !== "DynamicPromptBatcher") return;

    node.serialize_widgets = true;

    // Ensure prompt_1 widget exists and hide it
    let prompt1 = node.widgets.find(w => w.name === "prompt_1");
    if (!prompt1) {
      prompt1 = node.addWidget("text", "prompt_1", "", null, { multiline: true });
    }
    prompt1.hidden = true;
    if (prompt1.inputEl) prompt1.inputEl.style.display = "none";

    // Build DOM UI
    const wrapper = document.createElement("div");
    wrapper.style.display = "flex";
    wrapper.style.flexDirection = "column";
    wrapper.style.gap = "8px";
    wrapper.style.width = "100%";

    const scroller = document.createElement("div");
    scroller.style.display = "flex";
    scroller.style.flexDirection = "column";
    scroller.style.gap = "8px";
    scroller.style.maxHeight = "220px";
    scroller.style.overflowY = "auto";
    scroller.style.paddingRight = "4px";

    const addBtn = document.createElement("button");
    addBtn.textContent = "Add Prompt";
    addBtn.style.width = "100%";
    addBtn.style.padding = "6px 8px";

    wrapper.appendChild(scroller);
    wrapper.appendChild(addBtn);

    node.addDOMWidget("prompt_scroller", "custom", wrapper);

    const makeTextarea = (value, onInput) => {
      const ta = document.createElement("textarea");
      ta.value = value || "";
      ta.rows = 3;
      ta.style.width = "100%";
      ta.style.boxSizing = "border-box";
      ta.style.resize = "vertical";
      ta.style.minHeight = "60px";
      ta.style.maxHeight = "200px";
      ta.addEventListener("input", () => onInput(ta.value));
      return ta;
    };

    const ensureHiddenWidget = (index, value = "") => {
      const name = `prompt_${index}`;
      let w = node.widgets.find(x => x.name === name);
      if (!w) {
        w = node.addWidget("text", name, value, null, { multiline: true });
      }
      w.hidden = true;
      if (w.inputEl) w.inputEl.style.display = "none";
      w.value = value;
      return w;
    };

    const fitSizeToUI = () => {
      requestAnimationFrame(() => {
        const h = wrapper.offsetHeight || 240;
        const w = Math.max(node.size[0], 320);
        node.size = [w, h + 40]; // extra for title bar + padding
        node.setDirtyCanvas?.(true, true);
      });
    };

    const rebuild = () => {
      scroller.innerHTML = "";
      const promptWidgets = node.widgets
        .filter(w => w.name && w.name.startsWith("prompt_"))
        .map(w => ({ w, idx: parseInt(w.name.split("_")[1], 10) }))
        .filter(x => Number.isFinite(x.idx))
        .sort((a, b) => a.idx - b.idx);

      if (promptWidgets.length === 0) {
        promptWidgets.push({ w: prompt1, idx: 1 });
      }

      promptWidgets.forEach(({ w }) => {
        w.hidden = true;
        if (w.inputEl) w.inputEl.style.display = "none";
        const ta = makeTextarea(w.value || "", (val) => {
          w.value = val;
          node.setDirtyCanvas(true, true);
        });
        scroller.appendChild(ta);
      });

      fitSizeToUI();
    };

    addBtn.addEventListener("click", () => {
      const count = node.widgets.filter(w => w.name?.startsWith("prompt_")).length;
      const next = count + 1;
      const w = ensureHiddenWidget(next, "");
      const ta = makeTextarea("", (val) => {
        w.value = val;
        node.setDirtyCanvas(true, true);
      });
      scroller.appendChild(ta);
      scroller.scrollTop = scroller.scrollHeight;
      fitSizeToUI();
    });

    rebuild();

    node.onConfigure = () => {
      rebuild();
    };
  },
});
