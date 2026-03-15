"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.parseArgs = parseArgs;
function parseArgs(args) {
    const [, , time, genderString, sectString] = args;
    let gender = 1;
    if (genderString) {
        gender = Number.parseInt(genderString);
        if (isNaN(gender) || ![0, 1].includes(gender)) {
            throw new Error(`性别参数无效。男性传 1，女性传 0。`);
        }
    }
    let sect = 2;
    if (sectString) {
        sect = Number.parseInt(sectString);
        if (isNaN(sect) || ![1, 2].includes(sect)) {
            throw new Error(`早晚子时配置参数无效。传 1 表示 23:00-23:59 日干支为明天，传 2 表示 23:00-23:59 日干支为当天。`);
        }
    }
    return { time, gender, sect };
}
//# sourceMappingURL=util.js.map