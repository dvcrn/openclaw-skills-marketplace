#!/usr/bin/env node
/**
 * WALVIS walrus-sync script
 * Uploads and downloads space data to/from Walrus decentralized storage
 *
 * Usage:
 *   walrus-sync up [spaceId]    - upload space(s) to Walrus
 *   walrus-sync down <blobId>   - download and restore space from blob
 *   walrus-sync status          - show sync status of all spaces
 *   walrus-sync manifest-up     - upload manifest to Walrus
 */

import { readManifest, writeManifest, readSpace, writeSpace, listSpaceFiles, SPACES_DIR } from './storage.js';
import type { Space, WalrusUploadResponse, Manifest } from './types.js';
import { readFileSync } from 'fs';
import { join } from 'path';

const EPOCHS = 5; // store for 5 epochs on testnet

async function uploadToWalrus(data: string, publisher: string): Promise<string> {
  const res = await fetch(`${publisher}/v1/blobs?epochs=${EPOCHS}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: data,
  });

  if (!res.ok) {
    throw new Error(`Walrus upload failed: ${res.status} ${await res.text()}`);
  }

  const json = await res.json() as WalrusUploadResponse;
  const blobId = json.newlyCreated?.blobObject.blobId ?? json.alreadyCertified?.blobId;
  if (!blobId) throw new Error('No blob ID in Walrus response');
  return blobId;
}

async function downloadFromWalrus(blobId: string, aggregator: string): Promise<string> {
  const res = await fetch(`${aggregator}/v1/blobs/${blobId}`);
  if (!res.ok) {
    throw new Error(`Walrus download failed: ${res.status} ${await res.text()}`);
  }
  return res.text();
}

export async function syncSpaceUp(spaceId: string): Promise<string> {
  const manifest = readManifest();
  const space = readSpace(spaceId);
  const blobId = await uploadToWalrus(JSON.stringify(space), manifest.walrusPublisher);

  space.walrusBlobId = blobId;
  space.syncedAt = new Date().toISOString();
  writeSpace(space);

  manifest.spaces[spaceId] = { blobId, syncedAt: space.syncedAt };
  writeManifest(manifest);

  return blobId;
}

export async function syncSpaceDown(blobId: string): Promise<Space> {
  const manifest = readManifest();
  const raw = await downloadFromWalrus(blobId, manifest.walrusAggregator);
  const space = JSON.parse(raw) as Space;
  writeSpace(space);

  manifest.spaces[space.id] = { blobId, syncedAt: new Date().toISOString() };
  writeManifest(manifest);

  return space;
}

export async function syncManifestUp(): Promise<string> {
  const manifest = readManifest();
  const blobId = await uploadToWalrus(JSON.stringify(manifest), manifest.walrusPublisher);
  console.log(`Manifest uploaded. Blob ID: ${blobId}`);
  return blobId;
}

export async function syncStatus(): Promise<void> {
  const manifest = readManifest();
  const files = listSpaceFiles();

  if (files.length === 0) {
    console.log('No spaces found.');
    return;
  }

  console.log('\nWALVIS Sync Status\n==================');
  for (const file of files) {
    const space = JSON.parse(readFileSync(join(SPACES_DIR, file), 'utf-8')) as Space;
    const syncInfo = manifest.spaces[space.id];
    const itemCount = space.items.length;
    const synced = syncInfo ? `synced ${new Date(syncInfo.syncedAt).toLocaleString()}` : 'not synced';
    const blobId = syncInfo ? `blob: ${syncInfo.blobId.slice(0, 16)}...` : '';
    console.log(`  ${space.name} (${itemCount} items) - ${synced} ${blobId}`);
  }
  console.log('');
}

// CLI entry point
const [,, cmd, arg] = process.argv;

if (cmd === 'up') {
  const manifest = readManifest();
  const spaceIds = arg ? [arg] : Object.keys(manifest.spaces).length > 0
    ? listSpaceFiles().map(f => f.replace('.json', ''))
    : [manifest.activeSpace];

  for (const id of spaceIds) {
    try {
      const blobId = await syncSpaceUp(id);
      console.log(`✓ Synced space "${id}" -> blob: ${blobId}`);
    } catch (err) {
      console.error(`✗ Failed to sync "${id}": ${(err as Error).message}`);
    }
  }
} else if (cmd === 'down') {
  if (!arg) { console.error('Usage: walrus-sync down <blobId>'); process.exit(1); }
  try {
    const space = await syncSpaceDown(arg);
    console.log(`✓ Restored space "${space.name}" from blob ${arg}`);
  } catch (err) {
    console.error(`✗ Failed: ${(err as Error).message}`);
    process.exit(1);
  }
} else if (cmd === 'status') {
  await syncStatus();
} else if (cmd === 'manifest-up') {
  await syncManifestUp();
} else if (cmd) {
  console.error(`Unknown command: ${cmd}. Use: up | down | status | manifest-up`);
  process.exit(1);
}
