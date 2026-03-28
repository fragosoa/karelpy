'use strict';

// ────────────────────────────────────────────────────────────
// Constants
// ────────────────────────────────────────────────────────────

const DIR_LABELS = { NORTH: 'Norte', SOUTH: 'Sur', EAST: 'Este', WEST: 'Oeste' };

const DIR_ANGLE = { NORTH: 0, EAST: Math.PI / 2, SOUTH: Math.PI, WEST: -Math.PI / 2 };

const DEFAULT_CODE = `def gira_derecha():
    gira_izquierda()
    gira_izquierda()
    gira_izquierda()

def programa():
    while frente_libre():
        avanza()
    gira_derecha()
    while frente_libre():
        avanza()
    apagate()
`;

// ────────────────────────────────────────────────────────────
// WorldRenderer  —  draws Karel's world on a <canvas>
// ────────────────────────────────────────────────────────────

class WorldRenderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.cellSize = 48;
    this.worldWidth = 10;
    this.worldHeight = 10;
  }

  // Karel (col, row)  →  canvas top-left (x, y) of that cell
  toCanvas(col, row) {
    return {
      x: (col - 1) * this.cellSize,
      y: (this.worldHeight - row) * this.cellSize,
    };
  }

  // Recalculate cell size so the grid fits the wrapper
  resize(worldWidth, worldHeight) {
    this.worldWidth = worldWidth;
    this.worldHeight = worldHeight;

    const wrapper = this.canvas.parentElement;
    const maxW = wrapper.clientWidth  - 20;
    const maxH = wrapper.clientHeight - 20;
    this.cellSize = Math.max(
      18,
      Math.min(60, Math.floor(Math.min(maxW / worldWidth, maxH / worldHeight)))
    );
    this.canvas.width  = worldWidth  * this.cellSize;
    this.canvas.height = worldHeight * this.cellSize;
  }

  render(step, walls) {
    const ctx = this.ctx;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this._drawBackground();
    this._drawGrid();
    this._drawWalls(walls || []);
    this._drawBeepers(step.beepers || {});
    this._drawRobot(step.robot);
  }

  // ── Private drawing methods ────────────────────────────────

  _drawBackground() {
    this.ctx.fillStyle = '#ffffff';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
  }

  _drawGrid() {
    const { ctx, cellSize, worldWidth, worldHeight } = this;
    ctx.strokeStyle = '#ddd';
    ctx.lineWidth = 0.5;

    for (let c = 0; c <= worldWidth; c++) {
      ctx.beginPath();
      ctx.moveTo(c * cellSize, 0);
      ctx.lineTo(c * cellSize, worldHeight * cellSize);
      ctx.stroke();
    }
    for (let r = 0; r <= worldHeight; r++) {
      ctx.beginPath();
      ctx.moveTo(0, r * cellSize);
      ctx.lineTo(worldWidth * cellSize, r * cellSize);
      ctx.stroke();
    }

    // Coordinate labels (only if cells are big enough)
    if (cellSize >= 28) {
      ctx.fillStyle = '#ccc';
      ctx.font = `${Math.max(8, Math.floor(cellSize * 0.18))}px sans-serif`;
      ctx.textAlign = 'left';
      ctx.textBaseline = 'bottom';
      for (let col = 1; col <= worldWidth; col++) {
        for (let row = 1; row <= worldHeight; row++) {
          const { x, y } = this.toCanvas(col, row);
          ctx.fillText(`${col},${row}`, x + 2, y + cellSize - 1);
        }
      }
    }
  }

  _drawWalls(walls) {
    const { ctx, cellSize } = this;
    ctx.strokeStyle = '#111';
    ctx.lineWidth = Math.max(3, Math.floor(cellSize * 0.1));
    ctx.lineCap = 'square';

    for (const [col, row, dir] of walls) {
      const { x, y } = this.toCanvas(col, row);
      ctx.beginPath();
      switch (dir) {
        case 'NORTH': ctx.moveTo(x, y);            ctx.lineTo(x + cellSize, y);            break;
        case 'SOUTH': ctx.moveTo(x, y + cellSize); ctx.lineTo(x + cellSize, y + cellSize); break;
        case 'EAST':  ctx.moveTo(x + cellSize, y); ctx.lineTo(x + cellSize, y + cellSize); break;
        case 'WEST':  ctx.moveTo(x, y);            ctx.lineTo(x, y + cellSize);            break;
      }
      ctx.stroke();
    }
  }

  _drawBeepers(beepers) {
    const { ctx, cellSize } = this;
    const r = cellSize * 0.23;

    for (const [key, count] of Object.entries(beepers)) {
      const [col, row] = key.split(',').map(Number);
      const { x, y } = this.toCanvas(col, row);
      const cx = x + cellSize / 2;
      const cy = y + cellSize / 2;

      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.fillStyle = '#e67e22';
      ctx.fill();
      ctx.strokeStyle = '#b95a0a';
      ctx.lineWidth = 1.5;
      ctx.stroke();

      ctx.fillStyle = '#fff';
      ctx.font = `bold ${Math.max(9, Math.floor(cellSize * 0.28))}px sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(count > 99 ? '+' : String(count), cx, cy);
    }
  }

  _drawRobot({ col, row, dir }) {
    const { ctx, cellSize } = this;
    const { x, y } = this.toCanvas(col, row);
    const cx = x + cellSize / 2;
    const cy = y + cellSize / 2;
    const r  = cellSize * 0.32;

    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(DIR_ANGLE[dir]);

    // Triangle pointing up (= NORTH before rotation)
    ctx.beginPath();
    ctx.moveTo(0, -r);
    ctx.lineTo(-r * 0.7, r * 0.55);
    ctx.lineTo( r * 0.7, r * 0.55);
    ctx.closePath();

    ctx.fillStyle = '#2980b9';
    ctx.fill();
    ctx.strokeStyle = '#1a5f8a';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    ctx.restore();
  }
}

// ────────────────────────────────────────────────────────────
// KarelApp  —  main controller
// ────────────────────────────────────────────────────────────

class KarelApp {
  constructor() {
    this.steps       = [];
    this.currentStep = 0;
    this.playing     = false;
    this.playTimer   = null;

    // Initial world state (user-editable before running)
    this.worldBeepers = {};   // { "col,row": count }
    this.worldWalls   = [];   // [ [col, row, dir], ... ]

    this._initEditor();
    this._initCanvas();
    this._initControls();
    this._initConfigListeners();
    this._renderInitial();
  }

  // ── Initialisation ─────────────────────────────────────────

  _initEditor() {
    this.editor = CodeMirror.fromTextArea(
      document.getElementById('code-editor'),
      {
        mode: 'python',
        theme: 'monokai',
        lineNumbers: true,
        indentUnit: 4,
        tabSize: 4,
        indentWithTabs: false,
        autofocus: true,
        extraKeys: { Tab: 'indentMore', 'Shift-Tab': 'indentLess' },
      }
    );
    this.editor.setValue(DEFAULT_CODE);
  }

  _initCanvas() {
    this.canvas   = document.getElementById('world-canvas');
    this.renderer = new WorldRenderer(this.canvas);

    // Left-click → add beeper; right-click → remove beeper
    this.canvas.addEventListener('click',       (e) => this._onCanvasClick(e,  1));
    this.canvas.addEventListener('contextmenu', (e) => { e.preventDefault(); this._onCanvasClick(e, -1); });

    // Resize when the window changes
    window.addEventListener('resize', () => this._renderInitial());
  }

  _initControls() {
    document.getElementById('btn-run').addEventListener('click',   () => this.run());
    document.getElementById('btn-play').addEventListener('click',  () => this.togglePlay());
    document.getElementById('btn-back').addEventListener('click',  () => this.back());
    document.getElementById('btn-reset').addEventListener('click', () => this.reset());
    document.getElementById('btn-end').addEventListener('click',   () => this.end());
    document.getElementById('btn-clear-world').addEventListener('click', () => this.clearWorld());
  }

  _initConfigListeners() {
    const ids = ['cfg-width', 'cfg-height', 'cfg-col', 'cfg-row', 'cfg-dir', 'cfg-bag'];
    for (const id of ids) {
      document.getElementById(id).addEventListener('change', () => {
        this.steps = [];
        this._updateCounter();
        this._renderInitial();
      });
    }
  }

  // ── World config helpers ───────────────────────────────────

  _worldConfig() {
    return {
      width:   parseInt(document.getElementById('cfg-width').value)  || 10,
      height:  parseInt(document.getElementById('cfg-height').value) || 10,
      beepers: { ...this.worldBeepers },
      walls:   this.worldWalls,
    };
  }

  _robotConfig() {
    return {
      col:  parseInt(document.getElementById('cfg-col').value) || 1,
      row:  parseInt(document.getElementById('cfg-row').value) || 1,
      dir:  document.getElementById('cfg-dir').value,
      bag:  parseInt(document.getElementById('cfg-bag').value) || 0,
    };
  }

  // ── Canvas interaction ─────────────────────────────────────

  _onCanvasClick(e, delta) {
    const rect = this.canvas.getBoundingClientRect();
    const x    = e.clientX - rect.left;
    const y    = e.clientY - rect.top;
    const col  = Math.floor(x / this.renderer.cellSize) + 1;
    const row  = this.renderer.worldHeight - Math.floor(y / this.renderer.cellSize);
    const key  = `${col},${row}`;

    const current = this.worldBeepers[key] || 0;
    const next    = current + delta;
    if (next <= 0) {
      delete this.worldBeepers[key];
    } else {
      this.worldBeepers[key] = next;
    }

    // Reset steps so UI shows the new initial world
    this.steps = [];
    this._updateCounter();
    this._renderInitial();
  }

  clearWorld() {
    this.worldBeepers = {};
    this.worldWalls   = [];
    this.steps = [];
    this._updateCounter();
    this._renderInitial();
  }

  // ── Render helpers ─────────────────────────────────────────

  _renderInitial() {
    const world = this._worldConfig();
    const robot = this._robotConfig();
    this.renderer.resize(world.width, world.height);
    this.renderer.render({ robot, beepers: world.beepers }, world.walls);
    this._updateStatus({ robot, beepers: world.beepers });
  }

  _renderStep() {
    if (!this.steps.length) return;
    const step  = this.steps[this.currentStep];
    const world = this._worldConfig();
    this.renderer.render(step, world.walls);
    this._updateStatus(step);
  }

  // ── Run ────────────────────────────────────────────────────

  async run() {
    this.pause();
    this.hideError();

    const code  = this.editor.getValue();
    const world = this._worldConfig();
    const robot = this._robotConfig();

    const btn = document.getElementById('btn-run');
    btn.disabled    = true;
    btn.textContent = '⏳ Ejecutando…';

    try {
      const res  = await fetch('/api/run', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ code, world, robot }),
      });
      const data = await res.json();

      if (data.ok) {
        this.steps       = data.steps;
        this.currentStep = 0;
        this.renderer.resize(world.width, world.height);
        this._renderStep();
        this._updateCounter();
      } else {
        this.showError(data.error, data.line);
        this.steps = [];
        this._renderInitial();
      }
    } catch (err) {
      this.showError('Error de conexión: ' + err.message);
    } finally {
      btn.disabled    = false;
      btn.textContent = '▶ Ejecutar';
    }
  }

  // ── Playback ───────────────────────────────────────────────

  togglePlay() {
    this.playing ? this.pause() : this.play();
  }

  play() {
    if (!this.steps.length) return;
    if (this.currentStep >= this.steps.length - 1) this.currentStep = 0;
    this.playing = true;
    document.getElementById('btn-play').textContent = '⏸';
    this._tick();
  }

  pause() {
    this.playing = false;
    if (this.playTimer) { clearTimeout(this.playTimer); this.playTimer = null; }
    document.getElementById('btn-play').textContent = '▶';
  }

  _tick() {
    if (!this.playing) return;
    if (this.currentStep >= this.steps.length - 1) { this.pause(); return; }
    this.currentStep++;
    this._renderStep();
    this._updateCounter();
    const speed = parseInt(document.getElementById('speed-slider').value);
    this.playTimer = setTimeout(() => this._tick(), Math.round(1000 / speed));
  }

  back() {
    this.pause();
    if (this.currentStep > 0) {
      this.currentStep--;
      this._renderStep();
      this._updateCounter();
    }
  }

  reset() {
    this.pause();
    this.currentStep = 0;
    this.steps.length ? this._renderStep() : this._renderInitial();
    this._updateCounter();
  }

  end() {
    this.pause();
    if (this.steps.length) {
      this.currentStep = this.steps.length - 1;
      this._renderStep();
      this._updateCounter();
    }
  }

  // ── UI updates ─────────────────────────────────────────────

  _updateStatus({ robot }) {
    const { col, row, dir, bag } = robot;
    const bagLabel = bag === -1
      ? 'infinita'
      : `${bag} zumbador${bag !== 1 ? 'es' : ''}`;
    document.getElementById('status-bar').textContent =
      `Karel en (${col}, ${row})  ·  mirando al ${DIR_LABELS[dir]}  ·  mochila: ${bagLabel}`;
  }

  _updateCounter() {
    const total   = Math.max(0, this.steps.length - 1);
    const current = this.steps.length ? this.currentStep : 0;
    document.getElementById('step-counter').textContent = `Paso ${current} / ${total}`;
  }

  showError(message, line) {
    const panel = document.getElementById('error-panel');
    panel.textContent = line ? `Línea ${line}: ${message}` : message;
    panel.classList.remove('hidden');
    clearTimeout(this._errorTimer);
    this._errorTimer = setTimeout(() => this.hideError(), 9000);
  }

  hideError() {
    document.getElementById('error-panel').classList.add('hidden');
  }
}

// ── Boot ────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => { window.app = new KarelApp(); });
