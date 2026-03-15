"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const cantian_tymext_1 = require("cantian-tymext");
const util_js_1 = require("./util.js");
const { time: lunarTime, gender, sect } = (0, util_js_1.parseArgs)(process.argv);
const bazi = (0, cantian_tymext_1.buildBaziFromLunar)({ lunarTime, gender, sect });
const md = (0, cantian_tymext_1.baziToMarkdown)(bazi);
console.log(md);
//# sourceMappingURL=buildBaziFromLunar.js.map