/**
 * ==============================================================================
 * LIGHTWEIGHT OFFLINE CANVAS CHART ENGINE (0% External Dependencies)
 * Maintainer: Person 2 (Frontend JavaScript Engineer)
 * ==============================================================================
 * Renders crisp vertical bar charts, horizontal bar charts, and donut charts
 * directly on native HTML5 Canvas. Zero external CDN, zero internet required.
 * ==============================================================================
 */

const Charts = {
  // Official Government Palette
  palette: [
    '#1e3a8a', // Deep Blue
    '#047857', // Emerald Green
    '#b45309', // Amber / Gold
    '#0284c7', // Sky Blue
    '#7c3aed', // Violet
    '#b91c1c', // Crimson
    '#0d9488', // Teal
    '#475569', // Slate
    '#d97706', // Ocher
    '#4f46e5'  // Indigo
  ],

  _setupCanvas(canvas) {
    if (!canvas) return null;
    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();

    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    return { ctx, width: rect.width, height: rect.height };
  },

  /**
   * Horizontal Bar Chart (Ideal for long Ministry / Category names)
   */
  renderHorizontalBarChart(canvasTarget, labels, values) {
    const canvas = typeof canvasTarget === 'string' ? document.getElementById(canvasTarget) : canvasTarget;
    const setup = this._setupCanvas(canvas);
    if (!setup) return;
    const { ctx, width, height } = setup;

    ctx.clearRect(0, 0, width, height);

    if (!values || values.length === 0 || Math.max(...values, 0) === 0) {
      ctx.fillStyle = '#94a3b8';
      ctx.font = '12px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('No data available', width / 2, height / 2);
      return;
    }

    const padding = { top: 12, right: 35, bottom: 10, left: 160 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    const rowHeight = chartHeight / labels.length;
    const barHeight = Math.min(rowHeight * 0.6, 22);
    const maxValue = Math.max(...values, 1);

    labels.forEach((label, idx) => {
      const val = values[idx] || 0;
      const barWidth = (val / maxValue) * chartWidth;
      const y = padding.top + idx * rowHeight + (rowHeight - barHeight) / 2;

      // Draw truncated label on left
      ctx.fillStyle = '#1e293b';
      ctx.font = '11.5px sans-serif';
      ctx.textAlign = 'right';
      const cleanLabel = label.length > 26 ? label.slice(0, 25) + '…' : label;
      ctx.fillText(cleanLabel, padding.left - 10, y + barHeight / 2 + 4);

      // Draw horizontal bar
      ctx.fillStyle = this.palette[idx % this.palette.length];
      this._roundRect(ctx, padding.left, y, barWidth, barHeight, 3);

      // Value label on right of bar
      ctx.fillStyle = '#0f172a';
      ctx.font = 'bold 11px monospace';
      ctx.textAlign = 'left';
      ctx.fillText(val.toString(), padding.left + barWidth + 6, y + barHeight / 2 + 4);
    });
  },

  /**
   * Vertical Bar Chart
   */
  renderBarChart(canvasTarget, labels, values) {
    const canvas = typeof canvasTarget === 'string' ? document.getElementById(canvasTarget) : canvasTarget;
    const setup = this._setupCanvas(canvas);
    if (!setup) return;
    const { ctx, width, height } = setup;

    ctx.clearRect(0, 0, width, height);

    if (!values || values.length === 0 || Math.max(...values, 0) === 0) {
      ctx.fillStyle = '#94a3b8';
      ctx.font = '12px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('No data available', width / 2, height / 2);
      return;
    }

    const padding = { top: 20, right: 20, bottom: 45, left: 35 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;

    const maxValue = Math.max(...values, 1);
    const yMax = Math.ceil(maxValue * 1.2);
    const barSpacing = chartWidth / labels.length;
    const barWidth = Math.min(barSpacing * 0.55, 36);

    // Grid lines
    const gridLines = 4;
    ctx.strokeStyle = '#e2e8f0';
    ctx.lineWidth = 1;
    ctx.fillStyle = '#64748b';
    ctx.font = '10.5px monospace';
    ctx.textAlign = 'right';

    for (let i = 0; i <= gridLines; i++) {
      const yVal = Math.round((yMax / gridLines) * i);
      const yPos = padding.top + chartHeight - (chartHeight / gridLines) * i;

      ctx.beginPath();
      ctx.moveTo(padding.left, yPos);
      ctx.lineTo(width - padding.right, yPos);
      ctx.stroke();

      ctx.fillText(yVal.toString(), padding.left - 6, yPos + 3);
    }

    // Bars
    labels.forEach((label, idx) => {
      const val = values[idx] || 0;
      const barH = (val / yMax) * chartHeight;
      const x = padding.left + idx * barSpacing + (barSpacing - barWidth) / 2;
      const y = padding.top + chartHeight - barH;

      ctx.fillStyle = this.palette[idx % this.palette.length];
      this._roundRect(ctx, x, y, barWidth, barH, 3);

      if (val > 0) {
        ctx.fillStyle = '#0f172a';
        ctx.font = 'bold 11px monospace';
        ctx.textAlign = 'center';
        ctx.fillText(val.toString(), x + barWidth / 2, y - 5);
      }

      ctx.fillStyle = '#334155';
      ctx.font = '11px sans-serif';
      ctx.textAlign = 'center';
      const cleanLabel = label.length > 9 ? label.slice(0, 8) + '…' : label;
      ctx.fillText(cleanLabel, x + barWidth / 2, height - padding.bottom + 16);
    });
  },

  /**
   * Donut Chart with Legend
   */
  renderDonutChart(canvasTarget, labels, values) {
    const canvas = typeof canvasTarget === 'string' ? document.getElementById(canvasTarget) : canvasTarget;
    const setup = this._setupCanvas(canvas);
    if (!setup) return;
    const { ctx, width, height } = setup;

    ctx.clearRect(0, 0, width, height);

    const total = values.reduce((sum, v) => sum + v, 0);
    if (total === 0) {
      ctx.fillStyle = '#94a3b8';
      ctx.font = '12px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('No data available', width / 2, height / 2);
      return;
    }

    const legendWidth = Math.min(width * 0.45, 180);
    const ringCenterX = (width - legendWidth) / 2;
    const ringCenterY = height / 2;
    const outerRadius = Math.min(ringCenterX - 12, ringCenterY - 12, 75);
    const innerRadius = outerRadius * 0.58;

    let startAngle = -Math.PI / 2;

    values.forEach((val, idx) => {
      if (val <= 0) return;
      const sliceAngle = (val / total) * (Math.PI * 2);
      const endAngle = startAngle + sliceAngle;

      ctx.beginPath();
      ctx.arc(ringCenterX, ringCenterY, outerRadius, startAngle, endAngle);
      ctx.arc(ringCenterX, ringCenterY, innerRadius, endAngle, startAngle, true);
      ctx.closePath();

      ctx.fillStyle = this.palette[idx % this.palette.length];
      ctx.fill();

      startAngle = endAngle;
    });

    // Center total number
    ctx.fillStyle = '#0f172a';
    ctx.font = 'bold 18px monospace';
    ctx.textAlign = 'center';
    ctx.fillText(total.toString(), ringCenterX, ringCenterY + 3);

    ctx.fillStyle = '#64748b';
    ctx.font = '9px sans-serif';
    ctx.fillText('SCHEMES', ringCenterX, ringCenterY + 16);

    // Legend
    const legendX = width - legendWidth + 8;
    const legendStartY = Math.max(10, (height - (labels.length * 20)) / 2);

    labels.forEach((label, idx) => {
      const y = legendStartY + idx * 21;
      const val = values[idx] || 0;

      ctx.fillStyle = this.palette[idx % this.palette.length];
      ctx.fillRect(legendX, y, 9, 9);

      ctx.fillStyle = '#1e293b';
      ctx.font = '11px sans-serif';
      ctx.textAlign = 'left';
      const cleanLabel = label.length > 18 ? label.slice(0, 17) + '…' : label;
      ctx.fillText(`${cleanLabel} (${val})`, legendX + 14, y + 8);
    });
  },

  _roundRect(ctx, x, y, width, height, radius) {
    if (height <= 0 || width <= 0) return;
    const r = Math.min(radius, width / 2, height / 2);
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + width - r, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + r);
    ctx.lineTo(x + width, y + height - r);
    ctx.quadraticCurveTo(x + width, y + height, x + width - r, y + height);
    ctx.lineTo(x + r, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
    ctx.fill();
  }
};
