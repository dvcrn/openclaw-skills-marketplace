app.displayDialogs = DialogModes.NO;

function fail(message) {
  throw new Error(message);
}

function normalizeLayerName(name) {
  return String(name).replace(/^\s+|\s+$/g, "");
}

function findTextLayer(parent, name) {
  var requested = String(name);
  var normalizedRequested = normalizeLayerName(requested);
  var normalizedMatch = null;
  for (var i = 0; i < parent.layers.length; i++) {
    var layer = parent.layers[i];
    if (layer.typename === "ArtLayer" && layer.kind === LayerKind.TEXT) {
      var layerName = String(layer.name);
      if (layerName === requested) {
        return layer;
      }
      if (!normalizedMatch && normalizeLayerName(layerName) === normalizedRequested) {
        normalizedMatch = layer;
      }
    }
    if (layer.typename === "LayerSet") {
      var nested = findTextLayer(layer, name);
      if (nested) return nested;
    }
  }
  return normalizedMatch;
}

function listTextLayers(parent, out) {
  for (var i = 0; i < parent.layers.length; i++) {
    var layer = parent.layers[i];
    if (layer.typename === "ArtLayer" && layer.kind === LayerKind.TEXT) {
      out.push(String(layer.name));
    }
    if (layer.typename === "LayerSet") {
      listTextLayers(layer, out);
    }
  }
}

var inputPath = "__INPUT_PATH__";
var layerName = "__LAYER_NAME__";
var newText = "__NEW_TEXT__";
var outputPath = "__OUTPUT_PATH__";
var styleLock = "__STYLE_LOCK__" !== "false";
var inputPathLower = String(inputPath).toLowerCase();
var outputPathLower = String(outputPath).toLowerCase();
var saveInPlace = inputPathLower === outputPathLower;

var inputFile = new File(inputPath);
if (!inputFile.exists) {
  fail("E_FILE_NOT_FOUND: " + inputPath);
}

var doc = app.open(inputFile);
try {
  var layer = findTextLayer(doc, layerName);
  if (!layer) {
    var available = [];
    listTextLayers(doc, available);
    fail("E_LAYER_NOT_FOUND: " + layerName + " | AVAILABLE_LAYERS: " + available.join(", "));
  }

  var textItem = layer.textItem;
  var beforeText = textItem.contents;
  var beforeFont = String(textItem.font);
  var beforeSize = String(textItem.size);

  textItem.contents = newText;

  var afterFont = String(textItem.font);
  var afterSize = String(textItem.size);
  if (styleLock && (beforeFont !== afterFont || beforeSize !== afterSize)) {
    textItem.contents = beforeText;
    fail("E_STYLE_MISMATCH: font/size changed unexpectedly");
  }

  if (saveInPlace || /\.psb$/i.test(outputPathLower)) {
    // Keep large documents as PSB; avoid saveAs PSD 2GB limit.
    doc.save();
  } else {
    var outFile = new File(outputPath);
    var saveOpts = new PhotoshopSaveOptions();
    doc.saveAs(outFile, saveOpts, true, Extension.LOWERCASE);
  }
  doc.close(SaveOptions.DONOTSAVECHANGES);
} catch (e) {
  try {
    doc.close(SaveOptions.DONOTSAVECHANGES);
  } catch (_ignored) {}
  fail(String(e && e.message ? e.message : e));
}
