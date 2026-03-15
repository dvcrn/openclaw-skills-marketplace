app.displayDialogs = DialogModes.NO;

function fail(message) {
  throw new Error(message);
}

var inputPath = "__INPUT_PATH__";
var pngPath = "__PNG_PATH__";
var exportMode = "__EXPORT_MODE__";
var pngDir = "__PNG_DIR__";

function sanitizeFileName(name) {
  var value = String(name || "");
  value = value.replace(/[\\\/:\*\?"<>\|]/g, "_");
  value = value.replace(/^\s+|\s+$/g, "");
  return value || "layer";
}

function makeSaveForWebPngOptions() {
  var opts = new ExportOptionsSaveForWeb();
  opts.format = SaveDocumentType.PNG;
  opts.PNG8 = false;
  opts.transparency = true;
  opts.interlaced = false;
  opts.optimized = true;
  try {
    opts.includeProfile = false;
  } catch (_ignored) {}
  return opts;
}

function exportLayerSetsAsPng(doc, outputDirPath) {
  var outDir = new Folder(outputDirPath);
  if (!outDir.exists) {
    outDir.create();
  }

  var topLayers = [];
  var visibility = [];
  for (var i = 0; i < doc.layers.length; i++) {
    topLayers.push(doc.layers[i]);
    visibility.push(doc.layers[i].visible);
    doc.layers[i].visible = false;
  }

  var opts = makeSaveForWebPngOptions();
  var exported = 0;
  try {
    for (var j = 0; j < topLayers.length; j++) {
      var layer = topLayers[j];
      if (layer.typename !== "LayerSet") {
        continue;
      }
      layer.visible = true;
      var fileName = sanitizeFileName(layer.name) + ".png";
      var outFile = new File(outputDirPath + "/" + fileName);
      doc.exportDocument(outFile, ExportType.SAVEFORWEB, opts);
      layer.visible = false;
      exported += 1;
    }
  } finally {
    for (var k = 0; k < topLayers.length; k++) {
      topLayers[k].visible = visibility[k];
    }
  }

  if (exported === 0) {
    fail("E_EXPORT_FAILED: no LayerSet found for layer_sets export");
  }
}

var inputFile = new File(inputPath);
if (!inputFile.exists) {
  fail("E_FILE_NOT_FOUND: " + inputPath);
}

var doc = app.open(inputFile);
try {
  if (exportMode === "layer_sets") {
    exportLayerSetsAsPng(doc, pngDir);
  } else {
    var outFile = new File(pngPath);
    var opts = new PNGSaveOptions();
    doc.saveAs(outFile, opts, true, Extension.LOWERCASE);
  }
  doc.close(SaveOptions.DONOTSAVECHANGES);
} catch (e) {
  try {
    doc.close(SaveOptions.DONOTSAVECHANGES);
  } catch (_ignored) {}
  fail("E_EXPORT_FAILED: " + String(e && e.message ? e.message : e));
}
