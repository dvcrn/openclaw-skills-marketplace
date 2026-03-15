/**
 * BookNotes — Reading Notes & Book Tracker
 * @author @TheShadowRose
 * @license MIT
 */
const fs = require('fs');
const path = require('path');

class BookNotes {
  constructor(options = {}) {
    this.booksDir = options.booksDir || './books';
    this.listFile = options.listFile || path.join(this.booksDir, 'reading-list.json');
    if (!fs.existsSync(this.booksDir)) fs.mkdirSync(this.booksDir, { recursive: true });
  }

  addBook(title, author, totalChapters) {
    if (!title || !title.trim()) return { error: 'Title is required' };
    const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    if (!slug) return { error: 'Title must contain alphanumeric characters' };
    const dir = path.join(this.booksDir, slug);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    const meta = { title, author, slug, totalChapters, status: 'reading', started: new Date().toISOString().split('T')[0] };
    fs.writeFileSync(path.join(dir, 'metadata.json'), JSON.stringify(meta, null, 2));
    fs.writeFileSync(path.join(dir, 'notes.md'), `# ${title}\nBy ${author}\n\n`);
    this._updateList(meta);
    return meta;
  }

  addNote(titleOrSlug, chapter, note) {
    const slug = titleOrSlug.toLowerCase().replace(/[^a-z0-9]+/g, '-');
    const dir = path.join(this.booksDir, slug);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    const notesFile = path.join(dir, 'notes.md');
    const entry = `\n## Chapter ${chapter}\n\n${note}\n`;
    fs.appendFileSync(notesFile, entry);
    return { slug, chapter, wordCount: note.split(/\s+/).length };
  }

  addQuote(titleOrSlug, quote, page) {
    const slug = titleOrSlug.toLowerCase().replace(/[^a-z0-9]+/g, '-');
    const dir = path.join(this.booksDir, slug);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    const file = path.join(dir, 'quotes.md');
    const entry = `\n> ${quote}${page ? ' (p.' + page + ')' : ''}\n`;
    if (!fs.existsSync(file)) fs.writeFileSync(file, '# Quotes\n');
    fs.appendFileSync(file, entry);
    return { slug, quote: quote.substring(0, 50) + '...' };
  }

  getList() {
    try { return JSON.parse(fs.readFileSync(this.listFile, 'utf8')); } catch { return []; }
  }

  stats() {
    const list = this.getList();
    return {
      total: list.length,
      reading: list.filter(b => b.status === 'reading').length,
      finished: list.filter(b => b.status === 'finished').length,
      toRead: list.filter(b => b.status === 'to-read').length
    };
  }

  _updateList(meta) {
    const list = this.getList();
    const idx = list.findIndex(b => b.slug === meta.slug);
    if (idx >= 0) list[idx] = meta; else list.push(meta);
    fs.writeFileSync(this.listFile, JSON.stringify(list, null, 2));
  }
}

module.exports = { BookNotes };
