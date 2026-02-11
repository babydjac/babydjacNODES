import { app } from "../../../scripts/app.js";

const CATEGORY_COLORS = {
  Loaders: { color: "#f77f00", bgcolor: "#231408" },
  Latents: { color: "#3a86ff", bgcolor: "#0b1730" },
  Prompting: { color: "#2ec4b6", bgcolor: "#0b1f1d" },
  Analyze: { color: "#ff006e", bgcolor: "#2a0a1a" },
  Taglists: { color: "#8ac926", bgcolor: "#18240b" },
  Utils: { color: "#fb5607", bgcolor: "#2b1308" },
  default: { color: "#adb5bd", bgcolor: "#1a1d21" },
};

function getTopLevelCategory(category) {
  if (!category || typeof category !== "string") return null;
  if (!category.startsWith("babydjacNODES/")) return null;
  const parts = category.split("/");
  return parts.length > 1 ? parts[1] : null;
}

function applyCategoryColor(node, category) {
  let topLevel = getTopLevelCategory(category);
  if (topLevel === "Utility") topLevel = "Utils";
  if (!topLevel) return;
  const style = CATEGORY_COLORS[topLevel] || CATEGORY_COLORS.default;
  node.color = style.color;
  node.bgcolor = style.bgcolor;
  node.setDirtyCanvas?.(true, true);
}

app.registerExtension({
  name: "babydjacNODES.category_colors",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    const category = nodeData?.category;
    if (!getTopLevelCategory(category)) return;

    const onNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      onNodeCreated?.apply(this, arguments);
      applyCategoryColor(this, category);
    };

    const onConfigure = nodeType.prototype.onConfigure;
    nodeType.prototype.onConfigure = function () {
      const res = onConfigure?.apply(this, arguments);
      applyCategoryColor(this, category);
      return res;
    };
  },
});
