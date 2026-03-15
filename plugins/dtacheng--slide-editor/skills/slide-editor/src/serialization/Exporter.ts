import type { SlideInfo, ElementInfo, CropRect } from '../types';

export class Exporter {
  exportClean(): string {
    const clone = document.documentElement.cloneNode(true) as HTMLElement;

    // Remove editor UI elements
    clone.querySelectorAll('#slide-editor-toolbar').forEach((el) => el.remove());
    clone.querySelectorAll('#slide-editor-properties').forEach((el) => el.remove());
    clone.querySelectorAll('#slide-editor-navigator').forEach((el) => el.remove());
    clone.querySelectorAll('#slide-editor-styles').forEach((el) => el.remove());
    clone.querySelectorAll('.slide-editor-resize-handle').forEach((el) => el.remove());
    clone.querySelectorAll('.slide-editor-crop-overlay').forEach((el) => el.remove());

    // Remove editor classes
    clone.querySelectorAll('.slide-editor-selected').forEach((el) => {
      el.classList.remove('slide-editor-selected');
    });
    clone.querySelectorAll('.slide-editor-editing').forEach((el) => {
      el.classList.remove('slide-editor-editing');
    });

    // Remove data-editor-id attributes
    clone.querySelectorAll('[data-editor-id]').forEach((el) => {
      el.removeAttribute('data-editor-id');
    });

    // Remove contenteditable
    clone.querySelectorAll('[contenteditable]').forEach((el) => {
      el.removeAttribute('contenteditable');
    });

    // Remove editor script tag if present
    clone.querySelectorAll('script').forEach((script) => {
      if (script.textContent?.includes('__openclawEditor')) {
        script.remove();
      }
    });

    // Clean up inline styles that were added by editor
    clone.querySelectorAll('[style*="position: absolute"]').forEach((el) => {
      // Keep position styles if they were part of original design
      // This is a heuristic - might need refinement
    });

    return '<!DOCTYPE html>\n' + clone.outerHTML;
  }

  exportWithEditor(editorScript: string): string {
    const html = document.documentElement.outerHTML;

    // Ensure editor script is included
    if (!html.includes('__openclawEditor')) {
      const bodyClose = html.lastIndexOf('</body>');
      if (bodyClose > -1) {
        const scriptTag = `<script>${editorScript}</script>`;
        return '<!DOCTYPE html>\n' +
          html.slice(0, bodyClose) +
          scriptTag +
          '\n<script>window.__openclawEditor.enable();</script>\n' +
          html.slice(bodyClose);
      }
    }

    return '<!DOCTYPE html>\n' + html;
  }

  getSlides(): SlideInfo[] {
    const slides: SlideInfo[] = [];
    const slideElements = document.querySelectorAll('.slide');

    slideElements.forEach((slideEl, index) => {
      const elements = this.getSlideElements(slideEl as HTMLElement);
      slides.push({
        index,
        id: slideEl.id || `slide-${index}`,
        elements,
      });
    });

    return slides;
  }

  private getSlideElements(slideEl: HTMLElement): ElementInfo[] {
    const elements: ElementInfo[] = [];
    const editableElements = slideEl.querySelectorAll('[data-editor-id]');

    editableElements.forEach((el) => {
      const info = this.getElementInfo(el as HTMLElement, slideEl);
      if (info) elements.push(info);
    });

    return elements;
  }

  private getElementInfo(el: HTMLElement, slideEl: HTMLElement): ElementInfo | null {
    const id = el.getAttribute('data-editor-id');
    if (!id) return null;

    const rect = el.getBoundingClientRect();
    const slideRect = slideEl.getBoundingClientRect();

    return {
      id,
      type: this.getElementType(el),
      x: rect.left - slideRect.left,
      y: rect.top - slideRect.top,
      width: rect.width,
      height: rect.height,
      content: el.textContent || undefined,
      src: (el as HTMLImageElement).src || undefined,
      styles: this.extractStyles(el),
    };
  }

  private getElementType(el: HTMLElement): ElementInfo['type'] {
    const tagName = el.tagName.toLowerCase();
    if (tagName === 'img') return 'image';
    if (['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span', 'div', 'a', 'label'].includes(tagName)) {
      if (el.querySelector('img')) return 'unknown';
      return 'text';
    }
    if (tagName === 'svg' || el.closest('svg')) return 'shape';
    return 'unknown';
  }

  private extractStyles(el: HTMLElement): Record<string, string> {
    const computed = window.getComputedStyle(el);
    const styles: Record<string, string> = {};
    const relevantProps = [
      'fontSize', 'fontFamily', 'fontWeight', 'color', 'backgroundColor',
      'textAlign', 'lineHeight', 'opacity', 'borderRadius', 'padding', 'margin'
    ];

    relevantProps.forEach((prop) => {
      const value = computed.getPropertyValue(this.camelToKebab(prop));
      if (value && value !== 'none' && value !== 'normal') {
        styles[prop] = value;
      }
    });

    return styles;
  }

  private camelToKebab(str: string): string {
    return str.replace(/([a-z0-9])([A-Z])/g, '$1-$2').toLowerCase();
  }
}

export class ImageCropper {
  private overlay: HTMLDivElement | null = null;
  private cropArea: HTMLDivElement | null = null;
  private targetElement: HTMLElement | null = null;
  private onStart: ((rect: CropRect) => void) | null = null;
  private onCancel: (() => void) | null = null;

  startCrop(elementId: string, onApply: (rect: CropRect) => void, onCancel: () => void): void {
    this.targetElement = document.querySelector(`[data-editor-id="${elementId}"]`) as HTMLElement;
    if (!this.targetElement || this.targetElement.tagName.toLowerCase() !== 'img') {
      return;
    }

    this.onStart = onApply;
    this.onCancel = onCancel;

    this.createCropOverlay();
  }

  private createCropOverlay(): void {
    if (!this.targetElement) return;

    // Create overlay
    this.overlay = document.createElement('div');
    this.overlay.className = 'slide-editor-crop-overlay';
    this.overlay.innerHTML = `
      <div class="slide-editor-crop-controls">
        <button class="slide-editor-btn slide-editor-btn-primary" id="crop-apply">Apply Crop</button>
        <button class="slide-editor-btn" id="crop-cancel">Cancel</button>
      </div>
    `;

    // Create crop area
    this.cropArea = document.createElement('div');
    this.cropArea.className = 'slide-editor-crop-area';

    // Position overlay
    const rect = this.targetElement.getBoundingClientRect();
    this.overlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.7);
      z-index: 100000;
      display: flex;
      align-items: center;
      justify-content: center;
    `;

    // Create container for the image
    const container = document.createElement('div');
    container.style.cssText = `
      position: relative;
      width: ${rect.width}px;
      height: ${rect.height}px;
    `;

    // Clone the image
    const imgClone = this.targetElement.cloneNode(true) as HTMLImageElement;
    imgClone.style.cssText = `
      width: 100%;
      height: 100%;
      object-fit: contain;
    `;

    // Set up crop area
    this.cropArea.style.cssText = `
      position: absolute;
      top: 10%;
      left: 10%;
      width: 80%;
      height: 80%;
      border: 2px dashed var(--editor-accent, #00ffcc);
      background: transparent;
      cursor: move;
    `;

    container.appendChild(imgClone);
    container.appendChild(this.cropArea);
    this.overlay.appendChild(container);
    document.body.appendChild(this.overlay);

    // Add event listeners
    this.overlay.querySelector('#crop-apply')?.addEventListener('click', () => this.applyCrop());
    this.overlay.querySelector('#crop-cancel')?.addEventListener('click', () => this.cancelCrop());

    // Make crop area draggable
    this.setupCropDrag();
  }

  private setupCropDrag(): void {
    if (!this.cropArea) return;

    let isDragging = false;
    let startX = 0;
    let startY = 0;
    let startLeft = 0;
    let startTop = 0;

    this.cropArea.addEventListener('pointerdown', (e) => {
      isDragging = true;
      startX = e.clientX;
      startY = e.clientY;
      startLeft = this.cropArea!.offsetLeft;
      startTop = this.cropArea!.offsetTop;
      (e.target as HTMLElement).setPointerCapture(e.pointerId);
    });

    document.addEventListener('pointermove', (e) => {
      if (!isDragging || !this.cropArea) return;

      const deltaX = e.clientX - startX;
      const deltaY = e.clientY - startY;

      this.cropArea.style.left = `${startLeft + deltaX}px`;
      this.cropArea.style.top = `${startTop + deltaY}px`;
    });

    document.addEventListener('pointerup', () => {
      isDragging = false;
    });
  }

  private applyCrop(): void {
    if (!this.cropArea || !this.targetElement || !this.onStart) return;

    const imgRect = this.targetElement.getBoundingClientRect();
    const cropRect = this.cropArea.getBoundingClientRect();

    // Calculate relative crop coordinates (percentage)
    const rect: CropRect = {
      x: ((cropRect.left - imgRect.left) / imgRect.width) * 100,
      y: ((cropRect.top - imgRect.top) / imgRect.height) * 100,
      width: (cropRect.width / imgRect.width) * 100,
      height: (cropRect.height / imgRect.height) * 100,
    };

    // Apply CSS clip-path for non-destructive crop
    this.targetElement.style.clipPath = `inset(${rect.y}% ${100 - rect.x - rect.width}% ${100 - rect.y - rect.height}% ${rect.x}%)`;

    this.onStart(rect);
    this.cleanup();
  }

  private cancelCrop(): void {
    if (this.onCancel) {
      this.onCancel();
    }
    this.cleanup();
  }

  private cleanup(): void {
    this.overlay?.remove();
    this.overlay = null;
    this.cropArea = null;
    this.targetElement = null;
    this.onStart = null;
    this.onCancel = null;
  }
}
