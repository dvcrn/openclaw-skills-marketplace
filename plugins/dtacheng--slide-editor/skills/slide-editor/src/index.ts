import type { EditorAPI, EditorState, ElementInfo, SlideInfo, TextOptions, ImageOptions, CropRect, HistoryAction } from './types';
import { SelectionManager, DragManager, ResizeManager, TextEditor, HistoryManager } from './core';
import { Toolbar, PropertiesPanel, SlideNavigator } from './components';
import { Exporter, ImageCropper } from './serialization';
import { editorStyles } from './styles';

class SlideEditor implements EditorAPI {
  private state: EditorState;
  private selectionManager: SelectionManager;
  private dragManager: DragManager;
  private resizeManager: ResizeManager;
  private textEditor: TextEditor;
  private historyManager: HistoryManager;
  private toolbar: Toolbar;
  private propertiesPanel: PropertiesPanel;
  private slideNavigator: SlideNavigator;
  private exporter: Exporter;
  private imageCropper: ImageCropper;
  private styleElement: HTMLStyleElement | null = null;
  private idCounter = 0;
  private panelVisible = true;
  private originalFilePath: string | null = null;
  private currentTheme: 'auto' | 'light' | 'dark' = 'auto';

  constructor() {
    this.state = {
      enabled: false,
      selectedIds: new Set(),
      currentSlideIndex: 0,
      historyStack: [],
      historyIndex: 0,
    };

    this.historyManager = new HistoryManager(this.state);
    this.selectionManager = new SelectionManager(this.state);
    this.dragManager = new DragManager(this.state, (a) => this.pushHistory(a));
    this.resizeManager = new ResizeManager(this.state, (a) => this.pushHistory(a));
    this.textEditor = new TextEditor(this.state, (a) => this.pushHistory(a));
    this.exporter = new Exporter();
    this.imageCropper = new ImageCropper();

    this.toolbar = new Toolbar(this, {
      onExport: () => this.handleExport(),
      onAddText: () => this.handleAddText(),
      onAddImage: () => this.handleAddImage(),
      onTogglePanel: () => this.togglePanel(),
      onToggleTheme: () => this.toggleTheme(),
    });

    this.propertiesPanel = new PropertiesPanel(this);
    this.slideNavigator = new SlideNavigator(this);

    this.setupCallbacks();
    this.setupGlobalListeners();
  }

  private setupCallbacks(): void {
    this.selectionManager.setOnSelectionChange((selected) => {
      this.propertiesPanel.updateSelection(selected.length === 1 ? selected[0] : null);
      this.toolbar.updateUndoRedoState();

      // Update resize handles
      this.resizeManager.removeAllHandles();
      if (selected.length === 1) {
        this.resizeManager.createHandles(selected[0].id);
      }
    });

    this.dragManager.setOnDragEnd(() => {
      const selected = this.selectionManager.getSelectedIds();
      if (selected.length === 1) {
        this.resizeManager.updateHandlePositions(selected[0]);
      }
    });

    this.resizeManager.setOnResizeEnd(() => {
      this.toolbar.updateUndoRedoState();
    });

    this.textEditor.setOnEditEnd(() => {
      const activeId = this.textEditor.getActiveElement();
      if (activeId) {
        const el = this.getElementInfo(activeId);
        if (el) this.propertiesPanel.updateSelection(el);
      }
    });

    this.slideNavigator.setOnSlideChange((index) => {
      this.state.currentSlideIndex = index;
      this.selectionManager.deselectAll();
    });
  }

  private setupGlobalListeners(): void {
    document.addEventListener('pointermove', (e) => {
      if (this.dragManager.isActive()) {
        this.dragManager.handleMove(e);
      } else if (this.resizeManager.isActive()) {
        this.resizeManager.handleMove(e);
      }
    });

    document.addEventListener('pointerup', (e) => {
      this.dragManager.endDrag(e);
      this.resizeManager.endResize();
    });

    document.addEventListener('keydown', (e) => {
      // Undo/Redo
      if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
        e.preventDefault();
        if (e.shiftKey) {
          this.redo();
        } else {
          this.undo();
        }
        return;
      }

      // Save
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        this.handleSave();
        return;
      }

      // Toggle panel
      if (e.key === 'p' && !this.textEditor.isEditing()) {
        e.preventDefault();
        this.togglePanel();
        return;
      }

      // Toggle theme
      if (e.key === 't' && !this.textEditor.isEditing()) {
        e.preventDefault();
        this.toggleTheme();
        return;
      }

      // Delete
      if (e.key === 'Delete' || e.key === 'Backspace') {
        if (!this.textEditor.isEditing() && this.state.selectedIds.size > 0) {
          e.preventDefault();
          this.deleteSelected();
        }
      }

      // Escape
      if (e.key === 'Escape') {
        if (this.textEditor.isEditing()) {
          return; // Let TextEditor handle it
        }
        this.selectionManager.deselectAll();
      }
    });
  }

  // Toggle properties panel
  togglePanel(): void {
    this.panelVisible = !this.panelVisible;
    const panel = document.getElementById('slide-editor-properties');
    if (panel) {
      panel.classList.toggle('slide-editor-panel-hidden', !this.panelVisible);
    }
    document.body.classList.toggle('panel-hidden', !this.panelVisible);
  }

  // Toggle theme: light/dark mode
  toggleTheme(): void {
    // Cycle through: auto -> light -> dark -> auto
    if (this.currentTheme === 'auto') {
      this.currentTheme = 'light';
      document.body.classList.remove('slide-editor-dark');
      document.body.classList.add('slide-editor-light');
    } else if (this.currentTheme === 'light') {
      this.currentTheme = 'dark';
      document.body.classList.remove('slide-editor-light');
      document.body.classList.add('slide-editor-dark');
    } else {
      this.currentTheme = 'auto';
      document.body.classList.remove('slide-editor-light', 'slide-editor-dark');
    }
  }

  // Mode control
  enable(): void {
    if (this.state.enabled) return;
    this.state.enabled = true;

    // Inject styles
    this.styleElement = document.createElement('style');
    this.styleElement.id = 'slide-editor-styles';
    this.styleElement.textContent = editorStyles;
    document.head.appendChild(this.styleElement);

    // Mount UI
    const body = document.body;
    body.classList.add('slide-editor-active');
    if (!this.panelVisible) {
      body.classList.add('panel-hidden');
    }

    this.toolbar.mount(body);
    this.propertiesPanel.mount(body);
    this.slideNavigator.mount(body);

    // Make elements editable
    this.setupEditableElements();

    // Update initial state
    this.toolbar.updateUndoRedoState();
  }

  disable(): void {
    if (!this.state.enabled) return;
    this.state.enabled = false;

    // Remove styles
    this.styleElement?.remove();
    this.styleElement = null;

    // Unmount UI
    document.body.classList.remove('slide-editor-active');
    document.body.classList.remove('panel-hidden');
    this.toolbar.unmount();
    this.propertiesPanel.unmount();
    this.slideNavigator.unmount();

    // Remove handles and selection
    this.resizeManager.removeAllHandles();
    this.selectionManager.deselectAll();

    // Remove editable listeners
    this.removeEditableListeners();
  }

  isEnabled(): boolean {
    return this.state.enabled;
  }

  private setupEditableElements(): void {
    // Find all content elements in slides
    const selectors = [
      '.slide h1', '.slide h2', '.slide h3', '.slide h4', '.slide h5', '.slide h6',
      '.slide p', '.slide span', '.slide div:not(.slide):not([class*="slide"])',
      '.slide img'
    ];

    selectors.forEach((sel) => {
      document.querySelectorAll(sel).forEach((el) => {
        const htmlEl = el as HTMLElement;

        // Skip if already has editor id
        if (htmlEl.hasAttribute('data-editor-id')) return;

        // Skip very small or decorative elements
        const rect = htmlEl.getBoundingClientRect();
        if (rect.width < 10 || rect.height < 10) return;

        // Assign editor ID
        const id = `editor-el-${++this.idCounter}`;
        htmlEl.setAttribute('data-editor-id', id);

        // Ensure element is positioned for editing
        const computed = getComputedStyle(htmlEl);
        if (computed.position === 'static') {
          htmlEl.style.position = 'relative';
        }

        // Add event listeners
        this.addElementListeners(htmlEl, id);
      });
    });
  }

  private elementListeners: Map<HTMLElement, Map<string, (e: Event) => void>> = new Map();

  private addElementListeners(el: HTMLElement, id: string): void {
    const listeners = new Map<string, (e: Event) => void>();

    const onClick = (e: Event) => {
      if (!this.state.enabled) return;
      e.stopPropagation();
      const me = e as MouseEvent;
      const addToSelection = me.shiftKey;
      this.selectionManager.select(id, addToSelection);
    };

    const onDblClick = (e: Event) => {
      if (!this.state.enabled) return;
      e.stopPropagation();
      // Start text editing
      this.textEditor.startEditing(id);
    };

    const onPointerDown = (e: Event) => {
      if (!this.state.enabled) return;
      const pe = e as PointerEvent;
      // Start drag if this element is selected
      if (this.selectionManager.isSelected(id) && !this.textEditor.isEditing()) {
        this.dragManager.startDrag(pe, id);
      }
    };

    el.addEventListener('click', onClick);
    el.addEventListener('dblclick', onDblClick);
    el.addEventListener('pointerdown', onPointerDown);

    listeners.set('click', onClick);
    listeners.set('dblclick', onDblClick);
    listeners.set('pointerdown', onPointerDown);

    this.elementListeners.set(el, listeners);
  }

  private removeEditableListeners(): void {
    this.elementListeners.forEach((listeners, el) => {
      listeners.forEach((listener, event) => {
        el.removeEventListener(event, listener);
      });
    });
    this.elementListeners.clear();
  }

  // Query methods
  getSlides(): SlideInfo[] {
    return this.exporter.getSlides();
  }

  getSelectedElement(): ElementInfo | null {
    const ids = this.selectionManager.getSelectedIds();
    if (ids.length === 0) return null;
    return this.getElementInfo(ids[0]);
  }

  getSelectedElements(): ElementInfo[] {
    return this.selectionManager.getSelectedIds()
      .map((id) => this.getElementInfo(id))
      .filter((el): el is ElementInfo => el !== null);
  }

  getElementAt(x: number, y: number): ElementInfo | null {
    const el = document.elementFromPoint(x, y) as HTMLElement;
    if (!el) return null;

    const editorEl = el.closest('[data-editor-id]') as HTMLElement;
    if (!editorEl) return null;

    return this.getElementInfo(editorEl.getAttribute('data-editor-id') || '');
  }

  getElementById(id: string): ElementInfo | null {
    return this.getElementInfo(id);
  }

  private getElementInfo(id: string): ElementInfo | null {
    const el = document.querySelector(`[data-editor-id="${id}"]`) as HTMLElement;
    if (!el) return null;

    const slideEl = el.closest('.slide') as HTMLElement;
    const slideRect = slideEl?.getBoundingClientRect() || { left: 0, top: 0 };
    const rect = el.getBoundingClientRect();

    return {
      id,
      type: this.getElementType(el),
      x: rect.left - slideRect.left,
      y: rect.top - slideRect.top,
      width: rect.width,
      height: rect.height,
      content: el.textContent || undefined,
      src: (el as HTMLImageElement).src || undefined,
      styles: {},
    };
  }

  private getElementType(el: HTMLElement): ElementInfo['type'] {
    const tag = el.tagName.toLowerCase();
    if (tag === 'img') return 'image';
    if (['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span', 'a'].includes(tag)) return 'text';
    if (tag === 'svg' || el.closest('svg')) return 'shape';
    return 'unknown';
  }

  // Slide operations
  addSlide(index?: number): SlideInfo {
    const slides = document.querySelectorAll('.slide');
    const insertIndex = index ?? slides.length;

    // Create new slide element
    const newSlide = document.createElement('div');
    newSlide.className = 'slide';
    newSlide.id = `slide-${insertIndex}`;
    newSlide.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #666;">New Slide</div>';

    const slidesContainer = document.querySelector('.slides') || document.body;
    if (insertIndex < slides.length) {
      slides[insertIndex].before(newSlide);
    } else {
      slidesContainer.appendChild(newSlide);
    }

    this.pushHistory({ type: 'slide', from: null, to: { action: 'add', index: insertIndex } });
    this.slideNavigator.refresh();

    return {
      index: insertIndex,
      id: newSlide.id,
      elements: [],
    };
  }

  deleteSlide(index: number): void {
    const slides = document.querySelectorAll('.slide');
    if (index < 0 || index >= slides.length) return;

    const slide = slides[index];
    slide.remove();

    this.pushHistory({ type: 'slide', from: { index }, to: null });
    this.slideNavigator.refresh();

    // Adjust current slide index if needed
    if (this.state.currentSlideIndex >= slides.length - 1) {
      this.state.currentSlideIndex = Math.max(0, slides.length - 2);
    }
  }

  moveSlide(from: number, to: number): void {
    const slides = document.querySelectorAll('.slide');
    if (from < 0 || from >= slides.length || to < 0 || to >= slides.length) return;

    const slide = slides[from];
    const targetSlide = slides[to];

    if (from < to) {
      targetSlide.after(slide);
    } else {
      targetSlide.before(slide);
    }

    this.pushHistory({ type: 'slide', from: { index: from }, to: { index: to } });
    this.slideNavigator.refresh();
  }

  duplicateSlide(index: number): SlideInfo {
    const slides = document.querySelectorAll('.slide');
    if (index < 0 || index >= slides.length) {
      return this.addSlide();
    }

    const original = slides[index];
    const clone = original.cloneNode(true) as HTMLElement;

    // Re-assign editor IDs
    clone.querySelectorAll('[data-editor-id]').forEach((el) => {
      el.setAttribute('data-editor-id', `editor-el-${++this.idCounter}`);
    });

    original.after(clone);

    this.pushHistory({ type: 'slide', from: { index }, to: { action: 'duplicate' } });
    this.slideNavigator.refresh();

    return {
      index: index + 1,
      id: clone.id || `slide-${index + 1}`,
      elements: [],
    };
  }

  getCurrentSlide(): SlideInfo | null {
    const slides = document.querySelectorAll('.slide');
    const current = slides[this.state.currentSlideIndex];
    if (!current) return null;

    return {
      index: this.state.currentSlideIndex,
      id: current.id || `slide-${this.state.currentSlideIndex}`,
      elements: [],
    };
  }

  setCurrentSlide(index: number): void {
    const slides = document.querySelectorAll('.slide');
    if (index >= 0 && index < slides.length) {
      this.state.currentSlideIndex = index;
      this.slideNavigator.setActiveSlide(index);

      // Scroll to slide
      slides[index].scrollIntoView({ behavior: 'smooth' });
    }
  }

  // Element operations
  addText(options: TextOptions): ElementInfo {
    const slide = document.querySelector('.slide');
    if (!slide) {
      throw new Error('No slide found');
    }

    const id = `editor-el-${++this.idCounter}`;
    const textEl = document.createElement('div');

    textEl.setAttribute('data-editor-id', id);
    textEl.style.cssText = `
      position: absolute;
      left: ${options.x ?? 100}px;
      top: ${options.y ?? 100}px;
      width: ${options.width ?? 300}px;
      font-size: ${options.fontSize ?? '24px'};
      color: ${options.color ?? '#333'};
      font-weight: ${options.fontWeight ?? 'normal'};
      text-align: ${options.textAlign ?? 'left'};
      cursor: default;
    `;
    textEl.textContent = options.content ?? 'New Text';

    slide.appendChild(textEl);
    this.addElementListeners(textEl, id);

    this.pushHistory({ type: 'add', elementId: id, to: { type: 'text', options } });
    this.selectionManager.select(id);

    return this.getElementInfo(id)!;
  }

  addImage(options: ImageOptions): ElementInfo {
    const slide = document.querySelector('.slide');
    if (!slide) {
      throw new Error('No slide found');
    }

    const id = `editor-el-${++this.idCounter}`;
    const imgEl = document.createElement('img');

    imgEl.setAttribute('data-editor-id', id);
    imgEl.src = options.src;
    imgEl.alt = options.alt ?? '';
    imgEl.style.cssText = `
      position: absolute;
      left: ${options.x ?? 100}px;
      top: ${options.y ?? 100}px;
      width: ${options.width ?? 200}px;
      height: ${options.height ?? 'auto'};
      cursor: default;
    `;

    slide.appendChild(imgEl);
    this.addElementListeners(imgEl, id);

    this.pushHistory({ type: 'add', elementId: id, to: { type: 'image', options } });
    this.selectionManager.select(id);

    return this.getElementInfo(id)!;
  }

  deleteElement(id: string): void {
    const el = document.querySelector(`[data-editor-id="${id}"]`);
    if (!el) return;

    this.pushHistory({ type: 'delete', elementId: id, from: this.getElementInfo(id) });

    this.resizeManager.removeHandles(id);
    this.selectionManager.deselect(id);
    el.remove();
  }

  deleteSelected(): void {
    const ids = this.selectionManager.getSelectedIds();
    ids.forEach((id) => this.deleteElement(id));
  }

  moveElement(id: string, x: number, y: number): void {
    const el = document.querySelector(`[data-editor-id="${id}"]`) as HTMLElement;
    if (!el) return;

    const oldX = el.offsetLeft;
    const oldY = el.offsetTop;

    el.style.left = `${x}px`;
    el.style.top = `${y}px`;

    this.pushHistory({ type: 'move', elementId: id, from: { x: oldX, y: oldY }, to: { x, y } });
    this.resizeManager.updateHandlePositions(id);
  }

  resizeElement(id: string, width: number, height: number): void {
    const el = document.querySelector(`[data-editor-id="${id}"]`) as HTMLElement;
    if (!el) return;

    const oldWidth = el.offsetWidth;
    const oldHeight = el.offsetHeight;

    el.style.width = `${width}px`;
    el.style.height = `${height}px`;

    this.pushHistory({ type: 'resize', elementId: id, from: { width: oldWidth, height: oldHeight }, to: { width, height } });
    this.resizeManager.updateHandlePositions(id);
  }

  setTextContent(id: string, content: string): void {
    const el = document.querySelector(`[data-editor-id="${id}"]`);
    if (!el) return;

    const oldContent = el.innerHTML;
    el.innerHTML = content;

    this.pushHistory({ type: 'text', elementId: id, from: oldContent, to: content });
  }

  setStyle(id: string, styles: Record<string, string>): void {
    const el = document.querySelector(`[data-editor-id="${id}"]`) as HTMLElement;
    if (!el) return;

    const oldStyles: Record<string, string> = {};
    Object.keys(styles).forEach((key) => {
      oldStyles[key] = el.style.getPropertyValue(key);
      el.style.setProperty(key, styles[key]);
    });

    this.pushHistory({ type: 'style', elementId: id, from: oldStyles, to: styles });
    this.resizeManager.updateHandlePositions(id);
  }

  cropImage(id: string, rect: CropRect): void {
    const el = document.querySelector(`[data-editor-id="${id}"]`) as HTMLImageElement;
    if (!el || el.tagName.toLowerCase() !== 'img') return;

    el.style.clipPath = `inset(${rect.y}% ${100 - rect.x - rect.width}% ${100 - rect.y - rect.height}% ${rect.x}%)`;
    this.pushHistory({ type: 'crop', elementId: id, to: rect });
  }

  bringToFront(id: string): void {
    const el = document.querySelector(`[data-editor-id="${id}"]`) as HTMLElement;
    if (!el || !el.parentElement) return;

    el.parentElement.appendChild(el);
    this.resizeManager.updateHandlePositions(id);
  }

  sendToBack(id: string): void {
    const el = document.querySelector(`[data-editor-id="${id}"]`) as HTMLElement;
    if (!el || !el.parentElement) return;

    el.parentElement.insertBefore(el, el.parentElement.firstChild);
    this.resizeManager.updateHandlePositions(id);
  }

  // Selection
  selectElement(id: string, addToSelection = false): void {
    this.selectionManager.select(id, addToSelection);
  }

  deselectAll(): void {
    this.selectionManager.deselectAll();
  }

  // History
  private pushHistory(action: HistoryAction): void {
    this.historyManager.push(action);
    this.toolbar.updateUndoRedoState();
  }

  undo(): void {
    const action = this.historyManager.undo();
    if (!action) return;

    this.applyUndo(action);
    this.toolbar.updateUndoRedoState();
  }

  redo(): void {
    const action = this.historyManager.redo();
    if (!action) return;

    this.applyRedo(action);
    this.toolbar.updateUndoRedoState();
  }

  private applyUndo(action: HistoryAction): void {
    if (!action.elementId) return;

    const el = document.querySelector(`[data-editor-id="${action.elementId}"]`) as HTMLElement;
    if (!el) return;

    switch (action.type) {
      case 'move':
        if (action.from) {
          el.style.left = `${(action.from as { x: number }).x}px`;
          el.style.top = `${(action.from as { y: number }).y}px`;
        }
        break;
      case 'resize':
        if (action.from) {
          const f = action.from as { width: number; height: number; x?: number; y?: number };
          el.style.width = `${f.width}px`;
          el.style.height = `${f.height}px`;
          if (f.x !== undefined) el.style.left = `${f.x}px`;
          if (f.y !== undefined) el.style.top = `${f.y}px`;
        }
        break;
      case 'text':
        if (action.from !== undefined) {
          el.innerHTML = action.from as string;
        }
        break;
      case 'style':
        if (action.from) {
          Object.entries(action.from as Record<string, string>).forEach(([key, value]) => {
            el.style.setProperty(key, value);
          });
        }
        break;
    }

    this.resizeManager.updateHandlePositions(action.elementId);
  }

  private applyRedo(action: HistoryAction): void {
    if (!action.elementId) return;

    const el = document.querySelector(`[data-editor-id="${action.elementId}"]`) as HTMLElement;
    if (!el) return;

    switch (action.type) {
      case 'move':
        if (action.to) {
          el.style.left = `${(action.to as { x: number }).x}px`;
          el.style.top = `${(action.to as { y: number }).y}px`;
        }
        break;
      case 'resize':
        if (action.to) {
          const t = action.to as { width: number; height: number; x?: number; y?: number };
          el.style.width = `${t.width}px`;
          el.style.height = `${t.height}px`;
          if (t.x !== undefined) el.style.left = `${t.x}px`;
          if (t.y !== undefined) el.style.top = `${t.y}px`;
        }
        break;
      case 'text':
        if (action.to !== undefined) {
          el.innerHTML = action.to as string;
        }
        break;
      case 'style':
        if (action.to) {
          Object.entries(action.to as Record<string, string>).forEach(([key, value]) => {
            el.style.setProperty(key, value);
          });
        }
        break;
    }

    this.resizeManager.updateHandlePositions(action.elementId);
  }

  canUndo(): boolean {
    return this.historyManager.canUndo();
  }

  canRedo(): boolean {
    return this.historyManager.canRedo();
  }

  // Export
  export(): string {
    return this.exporter.exportClean();
  }

  exportWithEditor(): string {
    // This would need the bundled script content
    return this.exporter.exportWithEditor('');
  }

  // Set original file path for save functionality
  setOriginalFilePath(path: string): void {
    this.originalFilePath = path;
  }

  // Private helpers
  private handleExport(): void {
    const html = this.export();
    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = this.originalFilePath?.split('/').pop() || 'presentation.html';
    a.click();

    URL.revokeObjectURL(url);
  }

  private handleSave(): void {
    // Save the current state back to the original file (without editor)
    const html = this.export();

    // For browser environment, download the file
    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    const filename = this.originalFilePath?.split('/').pop() || 'presentation.html';
    a.download = filename;
    a.click();

    URL.revokeObjectURL(url);

    // Show save confirmation
    this.showToast(`Saved: ${filename}`);
  }

  private showToast(message: string): void {
    const toast = document.createElement('div');
    toast.className = 'slide-editor-toast';
    toast.textContent = message;
    toast.style.cssText = `
      position: fixed;
      bottom: 100px;
      left: 50%;
      transform: translateX(-50%);
      background: #22c55e;
      color: white;
      padding: 12px 24px;
      border-radius: 8px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 14px;
      font-weight: 500;
      z-index: 100001;
      animation: slide-editor-toast-in 0.3s ease;
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 2000);
  }

  private handleAddText(): void {
    this.addText({
      x: 100,
      y: 100,
      width: 300,
      content: 'New Text Block',
      fontSize: '32px',
    });
  }

  private handleAddImage(): void {
    // Create file input
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.style.display = 'none';

    input.addEventListener('change', (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = () => {
        const dataUrl = reader.result as string;
        this.addImage({
          x: 100,
          y: 100,
          src: dataUrl,
        });
      };
      reader.readAsDataURL(file);

      // Clean up
      input.remove();
    });

    document.body.appendChild(input);
    input.click();
  }
}

// Create global instance
const editor = new SlideEditor;

// Expose to window
declare global {
  interface Window {
    __openclawEditor: EditorAPI;
  }
}

window.__openclawEditor = editor;

// Auto-enable if ?edit=1 in URL
if (typeof window !== 'undefined') {
  const params = new URLSearchParams(window.location.search);
  if (params.get('edit') === '1') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => editor.enable());
    } else {
      editor.enable();
    }
  }

  // Listen for postMessage activation
  window.addEventListener('message', (event) => {
    if (event.data?.type === 'OPENCLAW_EDITOR_ENABLE') {
      editor.enable();
    } else if (event.data?.type === 'OPENCLAW_EDITOR_DISABLE') {
      editor.disable();
    }
  });
}

export { SlideEditor };
