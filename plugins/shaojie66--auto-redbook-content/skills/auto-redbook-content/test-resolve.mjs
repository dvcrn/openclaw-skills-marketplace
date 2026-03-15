import { resolve } from 'path';

const workdir = process.cwd();
const folderArg = '.';

const folder = folderArg ? resolve(workdir, folderArg) : null;

console.log('workdir:', workdir);
console.log('folderArg:', folderArg);
console.log('resolved folder:', folder);
