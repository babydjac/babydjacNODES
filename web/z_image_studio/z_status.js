import { app } from "../../../scripts/app.js";

app.registerExtension({
  name: "ZImageBase.StatusDisplay",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== "ZImagePromptEngineer") return;

    const onExecuted = nodeType.prototype.onExecuted;
    nodeType.prototype.onExecuted = function (message) {
      onExecuted?.apply(this, arguments);

      if (message && message.output && message.output.length >= 5) {
        const statusText = message.output[4];
        if (statusText) {
          this.title = `Z-Image Base Studio (${statusText})`;
        }
      }
    };

    const onDrawForeground = nodeType.prototype.onDrawForeground;
    nodeType.prototype.onDrawForeground = function (ctx) {
      onDrawForeground?.apply(this, arguments);
      ctx.save();
      ctx.font = "10px Arial";
      ctx.fillStyle = "#666";
      ctx.textAlign = "right";
      ctx.fillText("Target 80-230 words", this.size[0] - 10, this.size[1] - 10);
      ctx.restore();
    };
  },
});
