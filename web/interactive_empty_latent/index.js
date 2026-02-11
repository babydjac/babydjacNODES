import { app } from "../../../scripts/app.js";

app.registerExtension({
    name: "babydjac.interactive_empty_latent",

    async nodeCreated(node) {
        if (node.comfyClass !== "InteractiveEmptyLatent") return;

        node.size = [360, 440];

        const container = document.createElement("div");
        container.style.width = "100%";
        container.style.height = "308px";
        container.style.position = "relative";

        const canvas = document.createElement("canvas");
        canvas.width = 320;
        canvas.height = 260;
        canvas.style.border = "1px solid #333";
        canvas.style.cursor = "crosshair";
        canvas.style.width = "100%";
        canvas.style.height = "260px";
        canvas.style.display = "block";

        const readout = document.createElement("div");
        readout.style.fontSize = "12px";
        readout.style.color = "#d0d0d0";
        readout.style.marginTop = "8px";
        readout.style.fontFamily = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace";

        container.appendChild(canvas);
        container.appendChild(readout);
        node.addDOMWidget("resolution_graph", "custom", container);

        const ctx = canvas.getContext("2d");
        let dragging = false;
        let internalUpdate = false;
        let aspectRatio = 1.0;
        let cleanupDone = false;

        const getWidget = (name) => node.widgets?.find((w) => w?.name === name);
        const clamp = (v, minV, maxV) => Math.max(minV, Math.min(maxV, v));
        const toInt = (v, fallback = 0) => {
            const n = Number(v);
            return Number.isFinite(n) ? Math.round(n) : fallback;
        };

        const getMin = () => toInt(getWidget("width")?.options?.min, 64);
        const getMax = () => toInt(getWidget("width")?.options?.max, 2048);
        const getSnap = () => Math.max(1, toInt(getWidget("snap_to")?.value, 8));
        const getUiMode = () => String(getWidget("ui_mode")?.value ?? "graph");
        const isAspectLocked = () => Boolean(getWidget("aspect_lock")?.value);
        const getPreset = () => String(getWidget("preset")?.value ?? "custom");
        const getModelProfile = () => String(getWidget("model_profile")?.value ?? "SDXL");

        const MODEL_SNAP_DEFAULT = {
            "WAN 2.1 / WAN 2.2": 32,
            "SD 1.5": 64,
            SDXL: 64,
            "Z-Image / Z-Image Turbo": 16,
        };
        const MODEL_MAX_SIZE = {
            "WAN 2.1 / WAN 2.2": 1536,
            "SD 1.5": 1024,
            SDXL: 2048,
            "Z-Image / Z-Image Turbo": 2048,
        };

        const PROFILE_PRESETS = {
            "WAN 2.1 / WAN 2.2": {
                custom: null,
                "Low VRAM (480x480)": [480, 480],
                "Portrait Detail (480x832)": [480, 832],
                "Mid Detail (720x1280)": [720, 1280],
                "High Detail (1536x1536)": [1536, 1536],
            },
            "SD 1.5": {
                custom: null,
                "Base (512x512)": [512, 512],
                "High Quality (768x768)": [768, 768],
                "Landscape (768x512)": [768, 512],
                "Portrait (512x768)": [512, 768],
                "Wide (896x512)": [896, 512],
                "Tall (512x896)": [512, 896],
            },
            SDXL: {
                custom: null,
                "Base (1024x1024)": [1024, 1024],
                "Portrait (896x1152)": [896, 1152],
                "Landscape (1152x896)": [1152, 896],
                "Tall Portrait (768x1344)": [768, 1344],
                "Wide Landscape (1344x768)": [1344, 768],
                "Tall (768x1152)": [768, 1152],
                "Horizontal (1152x768)": [1152, 768],
            },
            "Z-Image / Z-Image Turbo": {
                custom: null,
                "Ultra Fast (512x512)": [512, 512],
                "Fast Square (720x720)": [720, 720],
                "Balanced Vertical (720x1280)": [720, 1280],
                "Balanced Square (1024x1024)": [1024, 1024],
                "High Quality (1344x1344)": [1344, 1344],
            },
        };

        const getWidth = () => toInt(getWidget("width")?.value, 1024);
        const getHeight = () => toInt(getWidget("height")?.value, 1024);

        const snapValue = (v) => {
            const minV = getMin();
            const maxV = getMax();
            const snapRaw = String(getWidget("snap_to")?.value ?? "auto");
            const snap = snapRaw === "auto" ? (MODEL_SNAP_DEFAULT[getModelProfile()] ?? 8) : getSnap();
            return clamp(Math.round(v / snap) * snap, minV, maxV);
        };

        const currentSnapForReadout = () => {
            const snapRaw = String(getWidget("snap_to")?.value ?? "auto");
            return snapRaw === "auto" ? (MODEL_SNAP_DEFAULT[getModelProfile()] ?? 8) : getSnap();
        };

        const syncWidthHeightWidgetStep = () => {
            const widthWidget = getWidget("width");
            const heightWidget = getWidget("height");
            const step = currentSnapForReadout();
            if (widthWidget?.options) widthWidget.options.step = step;
            if (heightWidget?.options) heightWidget.options.step = step;
        };

        const syncModelConstraints = () => {
            const widthWidget = getWidget("width");
            const heightWidget = getWidget("height");
            const modelMax = MODEL_MAX_SIZE[getModelProfile()] ?? 2048;
            const constrainedMax = clamp(modelMax, 64, 2048);
            if (widthWidget?.options) widthWidget.options.max = constrainedMax;
            if (heightWidget?.options) heightWidget.options.max = constrainedMax;
        };

        const setWH = (w, h) => {
            const widthWidget = getWidget("width");
            const heightWidget = getWidget("height");
            if (!widthWidget || !heightWidget) return;
            internalUpdate = true;
            widthWidget.value = snapValue(w);
            heightWidget.value = snapValue(h);
            internalUpdate = false;
        };

        const setPresetForCurrentSize = () => {
            const presetWidget = getWidget("preset");
            if (!presetWidget) return;
            const width = getWidth();
            const height = getHeight();
            const modelPresets = PROFILE_PRESETS[getModelProfile()] ?? { custom: null };
            const matched = Object.entries(modelPresets).find(([, size]) => size && size[0] === width && size[1] === height);
            internalUpdate = true;
            presetWidget.value = matched ? matched[0] : "custom";
            internalUpdate = false;
        };

        const getXY = () => {
            const minV = getMin();
            const maxV = getMax();
            const range = Math.max(1, maxV - minV);
            const x = ((getWidth() - minV) / range) * canvas.width;
            const y = canvas.height - ((getHeight() - minV) / range) * canvas.height;
            return { x: clamp(x, 0, canvas.width), y: clamp(y, 0, canvas.height) };
        };

        const drawAxes = () => {
            const minV = getMin();
            const maxV = getMax();
            ctx.strokeStyle = "#2f2f2f";
            ctx.lineWidth = 1;
            for (let i = 0; i <= 8; i++) {
                const x = (i / 8) * canvas.width;
                const y = (i / 8) * canvas.height;
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, canvas.height);
                ctx.stroke();
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(canvas.width, y);
                ctx.stroke();
            }
            ctx.fillStyle = "#9f9f9f";
            ctx.font = "11px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace";
            ctx.fillText(`W ${minV}`, 6, canvas.height - 6);
            ctx.fillText(`W ${maxV}`, canvas.width - 62, canvas.height - 6);
            ctx.fillText(`H ${maxV}`, 6, 14);
            ctx.fillText(`H ${minV}`, 6, canvas.height - 20);
        };

        const drawGraphMode = () => {
            const { x, y } = getXY();
            const bottomY = canvas.height;
            ctx.fillStyle = "rgba(79, 145, 255, 0.12)";
            ctx.fillRect(0, y, x, bottomY - y);
            ctx.strokeStyle = "rgba(79, 145, 255, 0.65)";
            ctx.lineWidth = 2;
            ctx.strokeRect(0.5, y + 0.5, Math.max(0, x - 1), Math.max(0, bottomY - y - 1));
            ctx.strokeStyle = "rgba(140, 200, 255, 0.85)";
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, canvas.height);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(canvas.width, y);
            ctx.stroke();
            ctx.fillStyle = "#5fc8ff";
            ctx.beginPath();
            ctx.arc(x, y, 6, 0, Math.PI * 2);
            ctx.fill();
        };

        const drawHistogramMode = () => {
            const { x, y } = getXY();
            const selectedW = clamp(x / canvas.width, 0, 1);
            const selectedH = clamp((canvas.height - y) / canvas.height, 0, 1);

            ctx.fillStyle = "rgba(52, 52, 52, 0.35)";
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            const bins = 28;
            const barW = canvas.width / bins;
            for (let i = 0; i < bins; i++) {
                const t = i / (bins - 1);
                const barHeight = (0.15 + 0.8 * selectedH) * (0.35 + 0.65 * Math.abs(1 - Math.abs(t - selectedW) * 2));
                const hPx = barHeight * canvas.height * 0.42;
                ctx.fillStyle = t <= selectedW ? "rgba(255, 184, 89, 0.8)" : "rgba(125, 97, 62, 0.35)";
                ctx.fillRect(i * barW + 1, canvas.height - hPx - 3, Math.max(1, barW - 2), hPx);
            }

            const rows = 20;
            const rowH = canvas.height / rows;
            for (let i = 0; i < rows; i++) {
                const t = i / (rows - 1);
                const rowWidth = (0.15 + 0.8 * selectedW) * (0.35 + 0.65 * Math.abs(1 - Math.abs(t - (1 - selectedH)) * 2));
                const wPx = rowWidth * canvas.width * 0.28;
                ctx.fillStyle = t >= 1 - selectedH ? "rgba(255, 184, 89, 0.8)" : "rgba(125, 97, 62, 0.35)";
                ctx.fillRect(2, i * rowH + 1, wPx, Math.max(1, rowH - 2));
            }

            ctx.strokeStyle = "rgba(255, 215, 153, 0.9)";
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, canvas.height);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(canvas.width, y);
            ctx.stroke();
            ctx.fillStyle = "#ffd991";
            ctx.beginPath();
            ctx.arc(x, y, 6, 0, Math.PI * 2);
            ctx.fill();
        };

        const render = () => {
            ctx.fillStyle = "#111";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            drawAxes();
            if (getUiMode() === "histogram") {
                drawHistogramMode();
            } else {
                drawGraphMode();
            }
            readout.textContent = `${getWidth()} x ${getHeight()} | latent ${Math.floor(getWidth() / 8)} x ${Math.floor(getHeight() / 8)} | snap ${currentSnapForReadout()} | ${getUiMode()} | ${getModelProfile()}`;
            node.setDirtyCanvas(true, true);
        };

        const applySize = (rawW, rawH, source = "graph") => {
            const minV = getMin();
            const maxV = getMax();
            let w = clamp(rawW, minV, maxV);
            let h = clamp(rawH, minV, maxV);
            const locked = isAspectLocked();

            if (locked && aspectRatio > 0) {
                if (source === "width") {
                    h = w / aspectRatio;
                } else if (source === "height") {
                    w = h * aspectRatio;
                } else {
                    const w1 = w;
                    const h1 = w1 / aspectRatio;
                    const h2 = h;
                    const w2 = h2 * aspectRatio;
                    const e1 = Math.abs(w1 - rawW) + Math.abs(h1 - rawH);
                    const e2 = Math.abs(w2 - rawW) + Math.abs(h2 - rawH);
                    if (e1 <= e2) {
                        w = w1;
                        h = h1;
                    } else {
                        w = w2;
                        h = h2;
                    }
                }
            }

            w = snapValue(w);
            h = snapValue(h);
            setWH(w, h);
            setPresetForCurrentSize();
            if (!locked && h > 0) {
                aspectRatio = w / h;
            }
            render();
        };

        const applyPreset = () => {
            const preset = getPreset();
            if (preset === "custom") {
                render();
                return;
            }
            const modelPresets = PROFILE_PRESETS[getModelProfile()] ?? { custom: null };
            const size = modelPresets[preset];
            if (!size) {
                render();
                return;
            }
            applySize(size[0], size[1], "preset");
        };

        const syncPresetOptionsFromModel = () => {
            const presetWidget = getWidget("preset");
            if (!presetWidget) return;
            const modelPresets = PROFILE_PRESETS[getModelProfile()] ?? { custom: null };
            const values = Object.keys(modelPresets);
            presetWidget.options = presetWidget.options || {};
            presetWidget.options.values = values;
            if (!values.includes(String(presetWidget.value))) {
                internalUpdate = true;
                presetWidget.value = "custom";
                internalUpdate = false;
            }
        };

        const updateFromPointer = (e) => {
            const rect = canvas.getBoundingClientRect();
            const px = clamp(e.clientX - rect.left, 0, rect.width);
            const py = clamp(e.clientY - rect.top, 0, rect.height);
            const nx = px / rect.width;
            const ny = 1 - py / rect.height;
            const minV = getMin();
            const maxV = getMax();
            const range = Math.max(1, maxV - minV);
            const snap = currentSnapForReadout();
            const rawW = minV + nx * range;
            const rawH = minV + ny * range;
            const snappedW = clamp(Math.round(rawW / snap) * snap, minV, maxV);
            const snappedH = clamp(Math.round(rawH / snap) * snap, minV, maxV);
            applySize(snappedW, snappedH, "graph");
        };

        const widthWidget = getWidget("width");
        const heightWidget = getWidget("height");
        const snapWidget = getWidget("snap_to");
        const modelWidget = getWidget("model_profile");
        const modeWidget = getWidget("ui_mode");
        const aspectWidget = getWidget("aspect_lock");
        const presetWidget = getWidget("preset");

        const wrapWidgetCallback = (widget, name) => {
            if (!widget || widget._latentSizeControllerWrapped) return;
            const original = widget.callback;
            widget._latentSizeControllerWrapped = true;
            widget.callback = function callback(value) {
                if (!internalUpdate) {
                    if (name === "width") {
                        applySize(toInt(value, getWidth()), getHeight(), "width");
                    } else if (name === "height") {
                        applySize(getWidth(), toInt(value, getHeight()), "height");
                    } else if (name === "model_profile") {
                        syncModelConstraints();
                        syncPresetOptionsFromModel();
                        syncWidthHeightWidgetStep();
                        applySize(getWidth(), getHeight(), "model_profile");
                    } else if (name === "preset") {
                        applyPreset();
                    } else if (name === "aspect_lock") {
                        if (Boolean(value) && getHeight() > 0) {
                            aspectRatio = getWidth() / getHeight();
                        }
                        render();
                    } else if (name === "snap_to") {
                        syncWidthHeightWidgetStep();
                        applySize(getWidth(), getHeight(), "snap_to");
                    } else {
                        applySize(getWidth(), getHeight(), name);
                    }
                }
                if (original) {
                    return original.apply(this, arguments);
                }
                return undefined;
            };
        };

        wrapWidgetCallback(widthWidget, "width");
        wrapWidgetCallback(heightWidget, "height");
        wrapWidgetCallback(modelWidget, "model_profile");
        wrapWidgetCallback(snapWidget, "snap_to");
        wrapWidgetCallback(modeWidget, "ui_mode");
        wrapWidgetCallback(aspectWidget, "aspect_lock");
        wrapWidgetCallback(presetWidget, "preset");

        // Quick orientation controls for fast width/height flipping.
        node.addWidget("button", "Horizontal", null, () => {
            const w = getWidth();
            const h = getHeight();
            if (h > w) {
                applySize(h, w, "orientation");
            } else {
                applySize(w, h, "orientation");
            }
        });
        node.addWidget("button", "Vertical", null, () => {
            const w = getWidth();
            const h = getHeight();
            if (w > h) {
                applySize(h, w, "orientation");
            } else {
                applySize(w, h, "orientation");
            }
        });

        const onPointerDown = (e) => {
            dragging = true;
            canvas.setPointerCapture(e.pointerId);
            updateFromPointer(e);
        };
        const onPointerMove = (e) => {
            if (dragging) updateFromPointer(e);
        };
        const onPointerUp = (e) => {
            dragging = false;
            try {
                canvas.releasePointerCapture(e.pointerId);
            } catch (err) {
                void err;
            }
        };

        canvas.addEventListener("pointerdown", onPointerDown);
        canvas.addEventListener("pointermove", onPointerMove);
        canvas.addEventListener("pointerup", onPointerUp);
        canvas.addEventListener("pointercancel", onPointerUp);
        canvas.addEventListener("pointerleave", onPointerUp);

        if (getHeight() > 0) {
            aspectRatio = getWidth() / getHeight();
        }
        syncModelConstraints();
        syncPresetOptionsFromModel();
        syncWidthHeightWidgetStep();
        applyPreset();
        applySize(getWidth(), getHeight(), "init");

        const originalRemoved = node.onRemoved;
        node.onRemoved = function onRemoved() {
            if (!cleanupDone) {
                cleanupDone = true;
                canvas.removeEventListener("pointerdown", onPointerDown);
                canvas.removeEventListener("pointermove", onPointerMove);
                canvas.removeEventListener("pointerup", onPointerUp);
                canvas.removeEventListener("pointercancel", onPointerUp);
                canvas.removeEventListener("pointerleave", onPointerUp);
            }
            if (originalRemoved) {
                return originalRemoved.apply(this, arguments);
            }
            return undefined;
        };
    }
});
