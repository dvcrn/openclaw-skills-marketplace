/**
 * WALVIS - Walrus Autonomous Learning & Vibe Intelligence System
 * TypeScript types for data model
 */

export type ItemType = 'link' | 'text' | 'image' | 'note';
export type ItemSource = 'telegram' | 'web' | 'manual';

export interface BookmarkItem {
  id: string;
  type: ItemType;
  url?: string;
  title: string;
  summary: string;
  tags: string[];
  content: string;
  screenshotBlobId?: string | null;
  notes: string;
  createdAt: string;
  updatedAt: string;
  source: ItemSource;
  analyzedBy: string;
}

export interface Space {
  id: string;
  name: string;
  description: string;
  items: BookmarkItem[];
  createdAt: string;
  updatedAt: string;
  walrusBlobId?: string;
  syncedAt?: string;
}

export interface ManifestItemIndex {
  spaceId: string;
  url?: string;
  title: string;
  screenshotBlobId?: string | null;
  tags: string[];
  updatedAt: string;
}

export interface ManifestSpaceEntry {
  name: string;
  blobId?: string;
  syncedAt?: string;
  updatedAt: string;
}

export interface Manifest {
  agent: string;
  activeSpace: string;
  network: string;
  walrusPublisher: string;
  walrusAggregator: string;
  spaces: Record<string, ManifestSpaceEntry>;
  items: Record<string, ManifestItemIndex>;
  manifestBlobId?: string;
  lastSyncAt?: string;
  suiAddress?: string;
  llmEndpoint?: string;
  llmModel?: string;
}

export interface AnalysisResult {
  title: string;
  summary: string;
  tags: string[];
  type: ItemType;
  content_snippet: string;
}

export interface WalrusUploadResponse {
  newlyCreated?: {
    blobObject: {
      blobId: string;
      id: string;
    };
  };
  alreadyCertified?: {
    blobId: string;
  };
}
