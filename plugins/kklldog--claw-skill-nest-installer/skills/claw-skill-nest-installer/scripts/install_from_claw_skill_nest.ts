#!/usr/bin/env node

import { mkdir, mkdtemp, rm, writeFile, copyFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { join, extname } from 'node:path';
import { homedir, tmpdir } from 'node:os';
import { spawn } from 'node:child_process';

type Skill = {
  id: string;
  name: string;
  originalName?: string;
};

const SKILLHUB_URL = process.env.SKILLHUB_URL ?? 'http://localhost:17890';
const SKILLHUB_API_KEY = process.env.SKILLHUB_API_KEY ?? 'claw-skill-nest-secret-key';
const SKILLS_DIR = join(homedir(), '.openclaw', 'workspace', 'skills');

function run(cmd: string, args: string[]): Promise<void> {
  return new Promise((resolve, reject) => {
    const child = spawn(cmd, args, { stdio: 'inherit' });
    child.on('error', reject);
    child.on('exit', (code) => {
      if (code === 0) resolve();
      else reject(new Error(`${cmd} exited with code ${code}`));
    });
  });
}

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${SKILLHUB_URL}${path}`, {
    headers: { 'X-API-Key': SKILLHUB_API_KEY },
  });
  if (!res.ok) {
    throw new Error(`请求失败: ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as T;
}

async function listSkills() {
  const skills = await apiGet<Skill[]>('/api/skills');
  console.log('Claw Skill Nest 上的可用 skills:');
  for (const name of skills.map((s) => s.name).sort()) {
    console.log(name);
  }
}

async function downloadSkillFile(skillId: string): Promise<Buffer> {
  const res = await fetch(`${SKILLHUB_URL}/api/skills/${skillId}/download`, {
    headers: { 'X-API-Key': SKILLHUB_API_KEY },
  });
  if (!res.ok) {
    throw new Error(`下载失败: ${res.status} ${res.statusText}`);
  }
  const arr = await res.arrayBuffer();
  return Buffer.from(arr);
}

async function extractZip(archivePath: string, targetDir: string): Promise<boolean> {
  try {
    if (process.platform === 'win32') {
      await run('powershell', [
        '-NoProfile',
        '-Command',
        `Expand-Archive -Path \"${archivePath}\" -DestinationPath \"${targetDir}\" -Force`,
      ]);
      return true;
    }

    if (existsSync('/usr/bin/unzip') || existsSync('/bin/unzip')) {
      await run('unzip', ['-o', archivePath, '-d', targetDir]);
      return true;
    }
  } catch {
    return false;
  }
  return false;
}

async function installSkill(skillName: string) {
  if (!skillName) throw new Error('请提供 skill 名称');

  console.log(`正在从 Claw Skill Nest 安装 skill: ${skillName}`);

  const skills = await apiGet<Skill[]>('/api/skills');
  const skill = skills.find((s) => s.name === skillName);
  if (!skill) {
    throw new Error(`未找到名为 ${skillName} 的 skill`);
  }

  const skillDir = join(SKILLS_DIR, skillName);
  await mkdir(skillDir, { recursive: true });

  const tmpRoot = await mkdtemp(join(tmpdir(), 'claw-skill-nest-'));
  const ext = extname(skill.originalName ?? '').toLowerCase() || '.bin';
  const tmpFile = join(tmpRoot, `download${ext}`);

  try {
    const fileBuf = await downloadSkillFile(skill.id);
    await writeFile(tmpFile, fileBuf);

    if (ext === '.zip') {
      const ok = await extractZip(tmpFile, skillDir);
      if (!ok) {
        const fallback = join(skillDir, skill.originalName || `${skillName}.zip`);
        await copyFile(tmpFile, fallback);
        console.log(`未找到可用解压工具，已保存压缩包: ${fallback}`);
      }
    } else {
      const fallback = join(skillDir, skill.originalName || `${skillName}${ext}`);
      await copyFile(tmpFile, fallback);
    }

    console.log(`Skill ${skillName} 安装成功到 ${skillDir}`);
  } finally {
    await rm(tmpRoot, { recursive: true, force: true });
  }
}

async function main() {
  await mkdir(SKILLS_DIR, { recursive: true });

  const command = process.argv[2];
  const skillName = process.argv[3];

  switch (command) {
    case '安装':
      await installSkill(skillName || '');
      break;
    case '更新':
      await installSkill(skillName || '');
      break;
    case '列出':
      await listSkills();
      break;
    default:
      console.log('用法: node scripts/install_from_claw_skill_nest.ts {安装|更新|列出} [skill名称]');
      process.exitCode = 1;
  }
}

main().catch((err) => {
  console.error(`错误: ${err.message}`);
  process.exit(1);
});
