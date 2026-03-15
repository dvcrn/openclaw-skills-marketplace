/**
 * types.mjs — Yijian type constants, classification, serialization & deserialization.
 *
 * Centralizes all type-related logic previously scattered across invoke.mjs
 * and skill-writer.mjs.
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

// ---------------------------------------------------------------------------
// 1. Type constants & classification
// ---------------------------------------------------------------------------

/** Basic scalar types — value is a plain string. */
export const BASIC_TYPES = ['String', 'TemplateString', 'Integer', 'Double', 'Boolean', 'Time'];

/** Complex object types — value needs JSON.stringify. */
export const COMPLEX_TYPES = ['Image', 'Detection', 'TrackDetection', 'Attribute', 'ROI', 'Tripwire'];

/** Inner types that can be wrapped in Array<T>. */
export const ARRAY_INNER_TYPES = [...BASIC_TYPES, ...COMPLEX_TYPES, 'Target'];

const _basicSet = new Set(BASIC_TYPES);
const _complexSet = new Set(COMPLEX_TYPES);
const _arrayInnerSet = new Set(ARRAY_INNER_TYPES);

/** Types whose output can be visualized (draw bbox / polygon / polyline). */
const _visualizableTypes = new Set(['Detection', 'TrackDetection', 'ROI', 'Tripwire']);

/** Types that represent input-side visual overlays (ROI, Tripwire). */
const _inputVisualizableTypes = new Set(['ROI', 'Tripwire']);

export function isBasicType(type) {
  return _basicSet.has(type);
}

export function isComplexType(type) {
  return _complexSet.has(type);
}

/**
 * Returns true if `type` is `Array<...>`.
 */
export function isArrayType(type) {
  return typeof type === 'string' && type.startsWith('Array<') && type.endsWith('>');
}

/**
 * Unwrap `Array<T>` → `T`. Returns `null` for non-array types.
 */
export function unwrapArrayType(type) {
  if (!isArrayType(type)) return null;
  return type.slice(6, -1); // strip "Array<" and ">"
}

/**
 * Returns true if the type is a visual/complex type (Image, Detection, etc.),
 * including Array-wrapped forms.
 */
export function isVisualType(type) {
  if (_complexSet.has(type)) return true;
  const inner = unwrapArrayType(type);
  return inner !== null && _complexSet.has(inner);
}

/**
 * Returns true if the type supports output visualization
 * (Detection, TrackDetection, ROI, Tripwire, and their Array<> forms).
 */
export function hasVisualization(type) {
  if (_visualizableTypes.has(type)) return true;
  const inner = unwrapArrayType(type);
  return inner !== null && _visualizableTypes.has(inner);
}

/**
 * Returns true if the type is an input-side visualizable overlay
 * (ROI, Tripwire, and their Array<> forms).
 */
export function isInputVisualizableType(type) {
  if (_inputVisualizableTypes.has(type)) return true;
  const inner = unwrapArrayType(type);
  return inner !== null && _inputVisualizableTypes.has(inner);
}

// ---------------------------------------------------------------------------
// 2. Field schema definitions
// ---------------------------------------------------------------------------

export const IMAGE_FIELDS = {
  imageId:      { type: 'String',  required: false },
  imageData:    { type: 'String',  required: false },
  sourceId:     { type: 'String',  required: false },
  imageWidth:   { type: 'Integer', required: false },
  imageHeight:  { type: 'Integer', required: false },
  timestamp:    { type: 'Integer', required: false },
};

export const DETECTION_FIELDS = {
  image_id:     { type: 'String',         required: false },
  source_id:    { type: 'String',         required: false },
  image_url:    { type: 'String',         required: false },
  description:  { type: 'String',         required: false },
  answers:      { type: 'Array<String>',  required: false },
  image_base64: { type: 'Array<String>',  required: false },
  predictions:  { type: 'Array<Object>',  required: false },
  roi_ids:      { type: 'Array<String>',  required: false },
  answer:       { type: 'String',         required: false },
};

/** TrackDetection shares the same schema as Detection. */
export const TRACK_DETECTION_FIELDS = DETECTION_FIELDS;

export const ATTRIBUTE_FIELDS = {
  image_id:     { type: 'String',         required: false },
  image_url:    { type: 'String',         required: false },
  description:  { type: 'String',         required: false },
  answer:       { type: 'Array<String>',  required: false },
  image_base64: { type: 'Array<String>',  required: false },
  predictions:  { type: 'Array<Object>',  required: false },
  roiIds:       { type: 'Array<String>',  required: false },
};

export const ROI_FIELDS = {
  id:           { type: 'String',        required: false },
  name:         { type: 'String',        required: false },
  displayName:  { type: 'String',        required: false },
  points:       { type: 'Array<Number>', required: true },
  iou:          { type: 'Float',         required: false, default: 0.0 },
  target_ratio: { type: 'Float',         required: false, default: 0.5 },
  kind:         { type: 'String',        required: true,  default: 'ROI' },
  interested:   { type: 'Boolean',       required: false, default: true },
  direction:    { type: 'String',        required: false },
  visuals:      { type: 'Object',        required: false },
};

export const TRIPWIRE_FIELDS = {
  id:           { type: 'String',        required: false },
  name:         { type: 'String',        required: false },
  displayName:  { type: 'String',        required: false },
  points:       { type: 'Array<Number>', required: true },
  iou:          { type: 'Float',         required: false, default: 0.0 },
  target_ratio: { type: 'Float',         required: false, default: 0.5 },
  kind:         { type: 'String',        required: true,  default: 'TripWire' },
  interested:   { type: 'Boolean',       required: false, default: true },
  direction:    { type: 'String',        required: true,  default: 'TwoWay' },
  visuals:      { type: 'Object',        required: false },
};

/** Lookup field schema by type name. */
export const FIELD_SCHEMAS = {
  Image:          IMAGE_FIELDS,
  Detection:      DETECTION_FIELDS,
  TrackDetection: TRACK_DETECTION_FIELDS,
  Attribute:      ATTRIBUTE_FIELDS,
  ROI:            ROI_FIELDS,
  Tripwire:       TRIPWIRE_FIELDS,
};

// ---------------------------------------------------------------------------
// 3. Serialization — buildValue(type, userValue)
// ---------------------------------------------------------------------------

/**
 * Simple heuristic to check if a string looks like base64-encoded data.
 */
function isBase64(str) {
  if (typeof str !== 'string' || str.length < 100) return false;
  return /^[A-Za-z0-9+/\n]+=*$/.test(str.trim());
}

/**
 * Parse image dimensions from buffer (supports JPEG and PNG).
 */
export function getImageDimensions(buffer) {
  // PNG: bytes 16-23 contain width and height in the IHDR chunk
  if (buffer[0] === 0x89 && buffer[1] === 0x50 && buffer[2] === 0x4E && buffer[3] === 0x47) {
    return {
      width: buffer.readUInt32BE(16),
      height: buffer.readUInt32BE(20),
    };
  }

  // JPEG: search for SOF markers
  if (buffer[0] === 0xFF && buffer[1] === 0xD8) {
    let offset = 2;
    while (offset < buffer.length - 1) {
      if (buffer[offset] !== 0xFF) { offset++; continue; }
      const marker = buffer[offset + 1];
      if (marker === 0xD9) break; // EOI
      if (marker >= 0xC0 && marker <= 0xCF && marker !== 0xC4 && marker !== 0xC8) {
        return {
          height: buffer.readUInt16BE(offset + 5),
          width: buffer.readUInt16BE(offset + 7),
        };
      }
      const segLen = buffer.readUInt16BE(offset + 2);
      offset += 2 + segLen;
    }
  }

  return { width: 0, height: 0 };
}

/**
 * Read an image file and return { base64, width, height }.
 */
export function readImageFile(filePath) {
  const resolved = path.resolve(filePath);
  if (!fs.existsSync(resolved)) {
    throw new Error(`Image file not found: ${resolved}`);
  }
  const buffer = fs.readFileSync(resolved);
  const { width, height } = getImageDimensions(buffer);
  return { base64: buffer.toString('base64'), width, height };
}

/**
 * Compute a short hash ID from the first 64 KB of a file.
 * Returns a stable 16-char hex string (MD5 prefix).
 */
export function fileHashId(filePath) {
  const fd = fs.openSync(path.resolve(filePath), 'r');
  const buf = Buffer.alloc(65536);
  const bytesRead = fs.readSync(fd, buf, 0, 65536, 0);
  fs.closeSync(fd);
  return crypto.createHash('md5').update(buf.subarray(0, bytesRead)).digest('hex').slice(0, 16);
}

/**
 * Build the Image value object and JSON-stringify it.
 */
function buildImageValue(userValue) {
  // (1) Pre-built object with imageData → pass through
  if (typeof userValue === 'object' && userValue !== null && userValue.imageData) {
    return JSON.stringify(userValue);
  }

  // (2) Object form { file, sourceId?, imageId?, timestamp? } or { image, sourceId?, imageId?, timestamp? } — for video frames
  if (typeof userValue === 'object' && userValue !== null && (userValue.file || userValue.image)) {
    const filePath = userValue.file || userValue.image;
    const img = readImageFile(filePath);
    return JSON.stringify({
      imageData: img.base64,
      imageId: userValue.imageId ?? fileHashId(filePath),
      sourceId: userValue.sourceId ?? fileHashId(filePath),
      imageWidth: img.width,
      imageHeight: img.height,
      timestamp: userValue.timestamp ?? Date.now(),
    });
  }

  // (3) String path or base64 (existing logic)
  let imageData, imageWidth = 0, imageHeight = 0;
  if (typeof userValue === 'string') {
    if (isBase64(userValue)) {
      imageData = userValue;
    } else {
      const img = readImageFile(userValue);
      imageData = img.base64;
      imageWidth = img.width;
      imageHeight = img.height;
    }
  } else {
    throw new Error(`Unsupported image value type: ${typeof userValue}`);
  }

  return JSON.stringify({
    imageData,
    imageId: '0',
    sourceId: '',
    imageWidth,
    imageHeight,
    timestamp: Date.now(),
  });
}

/**
 * Apply default values from a field schema to a user-provided object.
 */
function applyDefaults(obj, fields) {
  const result = { ...obj };
  for (const [key, def] of Object.entries(fields)) {
    if (result[key] === undefined && def.default !== undefined) {
      result[key] = def.default;
    }
  }
  return result;
}

/**
 * Build a ROI value: fill in defaults (kind='ROI', etc.), JSON.stringify.
 */
function buildROIValue(userValue) {
  if (typeof userValue === 'string') return userValue; // assume pre-serialized
  const obj = applyDefaults(userValue, ROI_FIELDS);
  return JSON.stringify(obj);
}

/**
 * Build a Tripwire value: fill in defaults (kind='TripWire', direction, etc.), JSON.stringify.
 */
function buildTripwireValue(userValue) {
  if (typeof userValue === 'string') return userValue;
  const obj = applyDefaults(userValue, TRIPWIRE_FIELDS);
  return JSON.stringify(obj);
}

/**
 * Build a complex object value (Detection, TrackDetection, Attribute).
 * If already an object, JSON.stringify; if string, assume pre-serialized.
 */
function buildGenericComplexValue(userValue) {
  if (typeof userValue === 'string') return userValue;
  return JSON.stringify(userValue);
}

/**
 * Unified entry point: serialize a user value based on its Yijian type.
 *
 * @param {string} type   - Yijian type (e.g. 'Image', 'ROI', 'Array<Detection>')
 * @param {*} userValue   - user-provided value
 * @returns {string}      - serialized string suitable for the API
 */
export function buildValue(type, userValue) {
  if (userValue === undefined || userValue === null) return '';

  // Array<T> — recurse on each element
  const inner = unwrapArrayType(type);
  if (inner !== null) {
    const arr = Array.isArray(userValue) ? userValue : [userValue];
    const built = arr.map(elem => {
      const s = buildValue(inner, elem);
      // For complex types the inner buildValue returns JSON string; parse it back
      // so the outer stringify produces a proper array.
      if (isComplexType(inner)) {
        try { return JSON.parse(s); } catch { return s; }
      }
      return s;
    });
    return JSON.stringify(built);
  }

  switch (type) {
    case 'Image':
      return buildImageValue(userValue);
    case 'ROI':
      return buildROIValue(userValue);
    case 'Tripwire':
      return buildTripwireValue(userValue);
    case 'Detection':
    case 'TrackDetection':
    case 'Attribute':
      return buildGenericComplexValue(userValue);
    default:
      // Basic types — convert to string
      if (typeof userValue === 'object') return JSON.stringify(userValue);
      return String(userValue);
  }
}

// ---------------------------------------------------------------------------
// 4. Deserialization — parseValue(type, valueString)
// ---------------------------------------------------------------------------

/**
 * Parse Detection / TrackDetection value string into structured results.
 * Extracts key fields from predictions.
 */
function parseDetections(value) {
  const images = JSON.parse(value);
  const detections = [];
  for (const image of images) {
    for (const pred of (image.predictions || [])) {
      detections.push({
        bbox: pred.bbox,
        confidence: pred.confidence,
        category: pred.categories && pred.categories.length > 0
          ? { id: pred.categories[0].id, name: pred.categories[0].name, confidence: pred.categories[0].confidence }
          : null,
        track_id: pred.track_id,
        area: pred.area,
      });
    }
  }
  return detections;
}

/**
 * Parse Attribute value string into structured results.
 * Similar to Detection but also extracts answer field.
 */
function parseAttributes(value) {
  const images = JSON.parse(value);
  const results = [];
  for (const image of images) {
    const entry = {
      answer: image.answer,
      predictions: [],
    };
    for (const pred of (image.predictions || [])) {
      entry.predictions.push({
        bbox: pred.bbox,
        confidence: pred.confidence,
        categories: pred.categories,
        answer: pred.answer,
      });
    }
    results.push(entry);
  }
  return results;
}

/**
 * Unified entry point: deserialize a value string based on its Yijian type.
 *
 * @param {string} type        - Yijian type
 * @param {string} valueString - raw value string from API response
 * @returns {*}                - parsed value
 */
export function parseValue(type, valueString) {
  if (valueString === undefined || valueString === null || valueString === '') return valueString;

  // Array<T>
  const inner = unwrapArrayType(type);
  if (inner !== null) {
    // For Detection/TrackDetection arrays the entire value is already the images array
    if (inner === 'Detection' || inner === 'TrackDetection') {
      return parseDetections(valueString);
    }
    if (inner === 'Attribute') {
      return parseAttributes(valueString);
    }
    // Generic array: parse, then recurse on each element
    const arr = JSON.parse(valueString);
    return arr.map(elem => {
      const s = typeof elem === 'string' ? elem : JSON.stringify(elem);
      return parseValue(inner, s);
    });
  }

  switch (type) {
    case 'Detection':
    case 'TrackDetection':
      // Single detection (wrapped in an array by API)
      return parseDetections(valueString);
    case 'Attribute':
      return parseAttributes(valueString);
    case 'ROI':
    case 'Tripwire':
      return JSON.parse(valueString);
    case 'Image':
      return JSON.parse(valueString);
    default:
      // Basic types — return as-is
      return valueString;
  }
}

/**
 * Post-process an outputs array: parse complex types and attach parsedValue.
 */
export function parseOutputs(outputs) {
  for (const field of outputs) {
    if (field.value && (isComplexType(field.type) || isArrayType(field.type))) {
      try {
        field.parsedValue = parseValue(field.type, field.value);
      } catch {
        // keep original value if parsing fails
      }
    }
  }
}

// ---------------------------------------------------------------------------
// 5. SKILL.md generation helpers
// ---------------------------------------------------------------------------

/**
 * Returns hints used when generating SKILL.md for a given type.
 */
export function getSkillMdHints(type) {
  const hints = {
    inputNote: null,
    hasVisualization: false,
    visualizationCmd: null,
  };

  // Check the raw type or inner type
  const inner = unwrapArrayType(type) || type;

  if (inner === 'Image') {
    hints.inputNote = '> pass a local file path (auto base64-encoded), or `{ file, sourceId?, imageId?, timestamp? }` / `{ image, sourceId?, imageId?, timestamp? }` for video frames — see **Video Frame Extraction Guide**.';
  } else if (inner === 'ROI') {
    hints.inputNote = '> requires drawing regions on the image — see **ROI / Tripwire Input Guide** below.';
  } else if (inner === 'Tripwire') {
    hints.inputNote = '> requires drawing tripwire lines on the image — see **ROI / Tripwire Input Guide** below.';
  }

  if (hasVisualization(type)) {
    hints.hasVisualization = true;
    if (inner === 'Detection' || inner === 'TrackDetection') {
      hints.visualizationCmd = 'visualize.mjs';
    } else if (inner === 'ROI' || inner === 'Tripwire') {
      hints.visualizationCmd = 'visualize.mjs';
    }
  }

  return hints;
}
