import type { EditorAPI, ElementInfo } from '../types';

export class PropertiesPanel {
  private container: HTMLDivElement;
  private editor: EditorAPI;
  private currentElement: ElementInfo | null = null;

  constructor(editor: EditorAPI) {
    this.editor = editor;
    this.container = this.createPanel();
  }

  private createPanel(): HTMLDivElement {
    const panel = document.createElement('div');
    panel.id = 'slide-editor-properties';
    panel.innerHTML = `
      <div class="slide-editor-panel-header">Properties</div>
      <div class="slide-editor-panel-content">
        <div class="slide-editor-no-selection">Select an element to edit</div>
        <div class="slide-editor-properties-form" style="display: none;">
          <div class="slide-editor-field-group">
            <label>Position</label>
            <div class="slide-editor-field-row">
              <div class="slide-editor-field">
                <span class="slide-editor-field-label">X</span>
                <input type="number" id="prop-x" step="1">
              </div>
              <div class="slide-editor-field">
                <span class="slide-editor-field-label">Y</span>
                <input type="number" id="prop-y" step="1">
              </div>
            </div>
          </div>
          <div class="slide-editor-field-group">
            <label>Size</label>
            <div class="slide-editor-field-row">
              <div class="slide-editor-field">
                <span class="slide-editor-field-label">W</span>
                <input type="number" id="prop-w" step="1" min="1">
              </div>
              <div class="slide-editor-field">
                <span class="slide-editor-field-label">H</span>
                <input type="number" id="prop-h" step="1" min="1">
              </div>
            </div>
          </div>
          <div class="slide-editor-field-group" id="text-properties" style="display: none;">
            <label>Text</label>
            <div class="slide-editor-field">
              <span class="slide-editor-field-label">Font Size</span>
              <input type="text" id="prop-font-size" placeholder="e.g. 24px">
            </div>
            <div class="slide-editor-field">
              <span class="slide-editor-field-label">Color</span>
              <input type="color" id="prop-color">
            </div>
            <div class="slide-editor-field">
              <span class="slide-editor-field-label">Weight</span>
              <select id="prop-font-weight">
                <option value="normal">Normal</option>
                <option value="bold">Bold</option>
                <option value="300">Light</option>
                <option value="600">Semi-Bold</option>
              </select>
            </div>
            <div class="slide-editor-field">
              <span class="slide-editor-field-label">Align</span>
              <select id="prop-text-align">
                <option value="left">Left</option>
                <option value="center">Center</option>
                <option value="right">Right</option>
              </select>
            </div>
          </div>
          <div class="slide-editor-field-group" id="image-properties" style="display: none;">
            <label>Image</label>
            <div class="slide-editor-field">
              <button class="slide-editor-btn slide-editor-btn-full" id="prop-crop">Crop Image</button>
            </div>
            <div class="slide-editor-field">
              <span class="slide-editor-field-label">Opacity</span>
              <input type="range" id="prop-opacity" min="0" max="100" value="100">
            </div>
          </div>
          <div class="slide-editor-field-group">
            <div class="slide-editor-field-row">
              <button class="slide-editor-btn" id="prop-bring-front">Bring to Front</button>
              <button class="slide-editor-btn" id="prop-send-back">Send to Back</button>
            </div>
          </div>
        </div>
      </div>
    `;

    this.setupEventListeners(panel);
    return panel;
  }

  private setupEventListeners(panel: HTMLElement): void {
    // Position inputs
    const xInput = panel.querySelector('#prop-x') as HTMLInputElement;
    const yInput = panel.querySelector('#prop-y') as HTMLInputElement;
    const wInput = panel.querySelector('#prop-w') as HTMLInputElement;
    const hInput = panel.querySelector('#prop-h') as HTMLInputElement;

    [xInput, yInput].forEach((input) => {
      input?.addEventListener('change', () => {
        if (this.currentElement) {
          this.editor.moveElement(
            this.currentElement.id,
            parseFloat(xInput.value) || 0,
            parseFloat(yInput.value) || 0
          );
        }
      });
    });

    [wInput, hInput].forEach((input) => {
      input?.addEventListener('change', () => {
        if (this.currentElement) {
          this.editor.resizeElement(
            this.currentElement.id,
            parseFloat(wInput.value) || 100,
            parseFloat(hInput.value) || 100
          );
        }
      });
    });

    // Text properties
    const fontSizeInput = panel.querySelector('#prop-font-size') as HTMLInputElement;
    const colorInput = panel.querySelector('#prop-color') as HTMLInputElement;
    const fontWeightSelect = panel.querySelector('#prop-font-weight') as HTMLSelectElement;
    const textAlignSelect = panel.querySelector('#prop-text-align') as HTMLSelectElement;

    fontSizeInput?.addEventListener('change', () => {
      if (this.currentElement) {
        this.editor.setStyle(this.currentElement.id, { fontSize: fontSizeInput.value });
      }
    });

    colorInput?.addEventListener('input', () => {
      if (this.currentElement) {
        this.editor.setStyle(this.currentElement.id, { color: colorInput.value });
      }
    });

    fontWeightSelect?.addEventListener('change', () => {
      if (this.currentElement) {
        this.editor.setStyle(this.currentElement.id, { fontWeight: fontWeightSelect.value });
      }
    });

    textAlignSelect?.addEventListener('change', () => {
      if (this.currentElement) {
        this.editor.setStyle(this.currentElement.id, { textAlign: textAlignSelect.value });
      }
    });

    // Image properties
    const opacityInput = panel.querySelector('#prop-opacity') as HTMLInputElement;
    opacityInput?.addEventListener('input', () => {
      if (this.currentElement) {
        const opacity = parseFloat(opacityInput.value) / 100;
        this.editor.setStyle(this.currentElement.id, { opacity: opacity.toString() });
      }
    });

    // Layer controls
    panel.querySelector('#prop-bring-front')?.addEventListener('click', () => {
      if (this.currentElement) {
        this.editor.bringToFront(this.currentElement.id);
      }
    });

    panel.querySelector('#prop-send-back')?.addEventListener('click', () => {
      if (this.currentElement) {
        this.editor.sendToBack(this.currentElement.id);
      }
    });
  }

  mount(parent: HTMLElement): void {
    parent.appendChild(this.container);
  }

  unmount(): void {
    this.container.remove();
  }

  updateSelection(element: ElementInfo | null): void {
    this.currentElement = element;
    const noSelection = this.container.querySelector('.slide-editor-no-selection');
    const form = this.container.querySelector('.slide-editor-properties-form') as HTMLElement;
    const textProps = this.container.querySelector('#text-properties') as HTMLElement;
    const imageProps = this.container.querySelector('#image-properties') as HTMLElement;

    if (!element) {
      noSelection?.classList.remove('slide-editor-hidden');
      form.style.display = 'none';
      return;
    }

    noSelection?.classList.add('slide-editor-hidden');
    form.style.display = 'block';

    // Update position
    (this.container.querySelector('#prop-x') as HTMLInputElement).value = Math.round(element.x).toString();
    (this.container.querySelector('#prop-y') as HTMLInputElement).value = Math.round(element.y).toString();
    (this.container.querySelector('#prop-w') as HTMLInputElement).value = Math.round(element.width).toString();
    (this.container.querySelector('#prop-h') as HTMLInputElement).value = Math.round(element.height).toString();

    // Show/hide type-specific properties
    textProps.style.display = element.type === 'text' ? 'block' : 'none';
    imageProps.style.display = element.type === 'image' ? 'block' : 'none';

    // Update text properties
    if (element.type === 'text') {
      (this.container.querySelector('#prop-font-size') as HTMLInputElement).value =
        element.styles.fontSize || '';
      (this.container.querySelector('#prop-color') as HTMLInputElement).value =
        this.rgbToHex(element.styles.color) || '#000000';
      (this.container.querySelector('#prop-font-weight') as HTMLSelectElement).value =
        element.styles.fontWeight || 'normal';
      (this.container.querySelector('#prop-text-align') as HTMLSelectElement).value =
        element.styles.textAlign || 'left';
    }

    // Update image properties
    if (element.type === 'image') {
      const opacity = parseFloat(element.styles.opacity || '1') * 100;
      (this.container.querySelector('#prop-opacity') as HTMLInputElement).value = opacity.toString();
    }
  }

  private rgbToHex(color: string): string {
    if (!color) return '#000000';
    if (color.startsWith('#')) return color;

    const match = color.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
    if (!match) return '#000000';

    const r = parseInt(match[1]).toString(16).padStart(2, '0');
    const g = parseInt(match[2]).toString(16).padStart(2, '0');
    const b = parseInt(match[3]).toString(16).padStart(2, '0');
    return `#${r}${g}${b}`;
  }
}
