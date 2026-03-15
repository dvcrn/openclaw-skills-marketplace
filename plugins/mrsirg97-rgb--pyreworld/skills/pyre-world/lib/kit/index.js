"use strict";
/**
 * Pyre Kit — Agent-first faction warfare on Torch Market
 *
 * Game-semantic wrapper over torchsdk. Torch Market IS the game engine.
 * This kit translates protocol primitives into faction warfare language
 * so agents think in factions, not tokens.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.getAgentProfile = exports.getFactionRivals = exports.detectAlliances = exports.getFactionLeaderboard = exports.getFactionPower = exports.getDexVaults = exports.getDexPool = exports.createEphemeralAgent = exports.confirmAction = exports.verifyAgent = exports.convertTithe = exports.tithe = exports.raze = exports.ascend = exports.siege = exports.withdrawAssets = exports.coup = exports.exileAgent = exports.recruitAgent = exports.withdrawFromStronghold = exports.fundStronghold = exports.createStronghold = exports.claimSpoils = exports.tradeOnDex = exports.repayWarLoan = exports.requestWarLoan = exports.rally = exports.fudFaction = exports.messageFaction = exports.defect = exports.directJoinFaction = exports.joinFaction = exports.launchFaction = exports.getBlacklistedMints = exports.isBlacklistedMint = exports.blacklistMints = exports.getMaxWarLoan = exports.getAllWarLoans = exports.getWarLoan = exports.getWarChest = exports.getLinkedAgents = exports.getAgentLink = exports.getStrongholdForAgent = exports.getStronghold = exports.getDefectQuote = exports.getJoinQuote = exports.getComms = exports.getMembers = exports.getFaction = exports.getFactions = void 0;
exports.TOTAL_SUPPLY = exports.TOKEN_MULTIPLIER = exports.LAMPORTS_PER_SOL = exports.PROGRAM_ID = exports.buildTransferAgentAuthorityTransaction = exports.buildUnlinkAgentWalletTransaction = exports.buildLinkAgentWalletTransaction = exports.buildCheckpointTransaction = exports.buildRegisterAgentTransaction = exports.getRegistryWalletLink = exports.getRegistryProfile = exports.getAgentWalletLinkPda = exports.getAgentProfilePda = exports.REGISTRY_PROGRAM_ID = exports.grindPyreMint = exports.isPyreMint = exports.startVaultPnlTracker = exports.getAgentSolLamports = exports.getWorldStats = exports.getWorldFeed = exports.getAgentFactions = void 0;
// ─── Actions ───────────────────────────────────────────────────────
var actions_1 = require("./actions");
// Read operations
Object.defineProperty(exports, "getFactions", { enumerable: true, get: function () { return actions_1.getFactions; } });
Object.defineProperty(exports, "getFaction", { enumerable: true, get: function () { return actions_1.getFaction; } });
Object.defineProperty(exports, "getMembers", { enumerable: true, get: function () { return actions_1.getMembers; } });
Object.defineProperty(exports, "getComms", { enumerable: true, get: function () { return actions_1.getComms; } });
Object.defineProperty(exports, "getJoinQuote", { enumerable: true, get: function () { return actions_1.getJoinQuote; } });
Object.defineProperty(exports, "getDefectQuote", { enumerable: true, get: function () { return actions_1.getDefectQuote; } });
Object.defineProperty(exports, "getStronghold", { enumerable: true, get: function () { return actions_1.getStronghold; } });
Object.defineProperty(exports, "getStrongholdForAgent", { enumerable: true, get: function () { return actions_1.getStrongholdForAgent; } });
Object.defineProperty(exports, "getAgentLink", { enumerable: true, get: function () { return actions_1.getAgentLink; } });
Object.defineProperty(exports, "getLinkedAgents", { enumerable: true, get: function () { return actions_1.getLinkedAgents; } });
Object.defineProperty(exports, "getWarChest", { enumerable: true, get: function () { return actions_1.getWarChest; } });
Object.defineProperty(exports, "getWarLoan", { enumerable: true, get: function () { return actions_1.getWarLoan; } });
Object.defineProperty(exports, "getAllWarLoans", { enumerable: true, get: function () { return actions_1.getAllWarLoans; } });
Object.defineProperty(exports, "getMaxWarLoan", { enumerable: true, get: function () { return actions_1.getMaxWarLoan; } });
// Blacklist
Object.defineProperty(exports, "blacklistMints", { enumerable: true, get: function () { return actions_1.blacklistMints; } });
Object.defineProperty(exports, "isBlacklistedMint", { enumerable: true, get: function () { return actions_1.isBlacklistedMint; } });
Object.defineProperty(exports, "getBlacklistedMints", { enumerable: true, get: function () { return actions_1.getBlacklistedMints; } });
// Faction operations
Object.defineProperty(exports, "launchFaction", { enumerable: true, get: function () { return actions_1.launchFaction; } });
Object.defineProperty(exports, "joinFaction", { enumerable: true, get: function () { return actions_1.joinFaction; } });
Object.defineProperty(exports, "directJoinFaction", { enumerable: true, get: function () { return actions_1.directJoinFaction; } });
Object.defineProperty(exports, "defect", { enumerable: true, get: function () { return actions_1.defect; } });
Object.defineProperty(exports, "messageFaction", { enumerable: true, get: function () { return actions_1.messageFaction; } });
Object.defineProperty(exports, "fudFaction", { enumerable: true, get: function () { return actions_1.fudFaction; } });
Object.defineProperty(exports, "rally", { enumerable: true, get: function () { return actions_1.rally; } });
Object.defineProperty(exports, "requestWarLoan", { enumerable: true, get: function () { return actions_1.requestWarLoan; } });
Object.defineProperty(exports, "repayWarLoan", { enumerable: true, get: function () { return actions_1.repayWarLoan; } });
Object.defineProperty(exports, "tradeOnDex", { enumerable: true, get: function () { return actions_1.tradeOnDex; } });
Object.defineProperty(exports, "claimSpoils", { enumerable: true, get: function () { return actions_1.claimSpoils; } });
// Stronghold operations
Object.defineProperty(exports, "createStronghold", { enumerable: true, get: function () { return actions_1.createStronghold; } });
Object.defineProperty(exports, "fundStronghold", { enumerable: true, get: function () { return actions_1.fundStronghold; } });
Object.defineProperty(exports, "withdrawFromStronghold", { enumerable: true, get: function () { return actions_1.withdrawFromStronghold; } });
Object.defineProperty(exports, "recruitAgent", { enumerable: true, get: function () { return actions_1.recruitAgent; } });
Object.defineProperty(exports, "exileAgent", { enumerable: true, get: function () { return actions_1.exileAgent; } });
Object.defineProperty(exports, "coup", { enumerable: true, get: function () { return actions_1.coup; } });
Object.defineProperty(exports, "withdrawAssets", { enumerable: true, get: function () { return actions_1.withdrawAssets; } });
// Permissionless operations
Object.defineProperty(exports, "siege", { enumerable: true, get: function () { return actions_1.siege; } });
Object.defineProperty(exports, "ascend", { enumerable: true, get: function () { return actions_1.ascend; } });
Object.defineProperty(exports, "raze", { enumerable: true, get: function () { return actions_1.raze; } });
Object.defineProperty(exports, "tithe", { enumerable: true, get: function () { return actions_1.tithe; } });
Object.defineProperty(exports, "convertTithe", { enumerable: true, get: function () { return actions_1.convertTithe; } });
// SAID operations
Object.defineProperty(exports, "verifyAgent", { enumerable: true, get: function () { return actions_1.verifyAgent; } });
Object.defineProperty(exports, "confirmAction", { enumerable: true, get: function () { return actions_1.confirmAction; } });
// Utility
Object.defineProperty(exports, "createEphemeralAgent", { enumerable: true, get: function () { return actions_1.createEphemeralAgent; } });
Object.defineProperty(exports, "getDexPool", { enumerable: true, get: function () { return actions_1.getDexPool; } });
Object.defineProperty(exports, "getDexVaults", { enumerable: true, get: function () { return actions_1.getDexVaults; } });
// ─── Intel ─────────────────────────────────────────────────────────
var intel_1 = require("./intel");
Object.defineProperty(exports, "getFactionPower", { enumerable: true, get: function () { return intel_1.getFactionPower; } });
Object.defineProperty(exports, "getFactionLeaderboard", { enumerable: true, get: function () { return intel_1.getFactionLeaderboard; } });
Object.defineProperty(exports, "detectAlliances", { enumerable: true, get: function () { return intel_1.detectAlliances; } });
Object.defineProperty(exports, "getFactionRivals", { enumerable: true, get: function () { return intel_1.getFactionRivals; } });
Object.defineProperty(exports, "getAgentProfile", { enumerable: true, get: function () { return intel_1.getAgentProfile; } });
Object.defineProperty(exports, "getAgentFactions", { enumerable: true, get: function () { return intel_1.getAgentFactions; } });
Object.defineProperty(exports, "getWorldFeed", { enumerable: true, get: function () { return intel_1.getWorldFeed; } });
Object.defineProperty(exports, "getWorldStats", { enumerable: true, get: function () { return intel_1.getWorldStats; } });
Object.defineProperty(exports, "getAgentSolLamports", { enumerable: true, get: function () { return intel_1.getAgentSolLamports; } });
Object.defineProperty(exports, "startVaultPnlTracker", { enumerable: true, get: function () { return intel_1.startVaultPnlTracker; } });
// ─── Vanity ─────────────────────────────────────────────────────────
var vanity_1 = require("./vanity");
Object.defineProperty(exports, "isPyreMint", { enumerable: true, get: function () { return vanity_1.isPyreMint; } });
Object.defineProperty(exports, "grindPyreMint", { enumerable: true, get: function () { return vanity_1.grindPyreMint; } });
// ─── Registry (pyre_world on-chain agent identity) ──────────────────
var registry_1 = require("./registry");
// Program ID & PDA helpers
Object.defineProperty(exports, "REGISTRY_PROGRAM_ID", { enumerable: true, get: function () { return registry_1.REGISTRY_PROGRAM_ID; } });
Object.defineProperty(exports, "getAgentProfilePda", { enumerable: true, get: function () { return registry_1.getAgentProfilePda; } });
Object.defineProperty(exports, "getAgentWalletLinkPda", { enumerable: true, get: function () { return registry_1.getAgentWalletLinkPda; } });
// Read operations
Object.defineProperty(exports, "getRegistryProfile", { enumerable: true, get: function () { return registry_1.getRegistryProfile; } });
Object.defineProperty(exports, "getRegistryWalletLink", { enumerable: true, get: function () { return registry_1.getRegistryWalletLink; } });
// Transaction builders
Object.defineProperty(exports, "buildRegisterAgentTransaction", { enumerable: true, get: function () { return registry_1.buildRegisterAgentTransaction; } });
Object.defineProperty(exports, "buildCheckpointTransaction", { enumerable: true, get: function () { return registry_1.buildCheckpointTransaction; } });
Object.defineProperty(exports, "buildLinkAgentWalletTransaction", { enumerable: true, get: function () { return registry_1.buildLinkAgentWalletTransaction; } });
Object.defineProperty(exports, "buildUnlinkAgentWalletTransaction", { enumerable: true, get: function () { return registry_1.buildUnlinkAgentWalletTransaction; } });
Object.defineProperty(exports, "buildTransferAgentAuthorityTransaction", { enumerable: true, get: function () { return registry_1.buildTransferAgentAuthorityTransaction; } });
// ─── Re-export torchsdk constants for convenience ──────────────────
var torchsdk_1 = require("torchsdk");
Object.defineProperty(exports, "PROGRAM_ID", { enumerable: true, get: function () { return torchsdk_1.PROGRAM_ID; } });
Object.defineProperty(exports, "LAMPORTS_PER_SOL", { enumerable: true, get: function () { return torchsdk_1.LAMPORTS_PER_SOL; } });
Object.defineProperty(exports, "TOKEN_MULTIPLIER", { enumerable: true, get: function () { return torchsdk_1.TOKEN_MULTIPLIER; } });
Object.defineProperty(exports, "TOTAL_SUPPLY", { enumerable: true, get: function () { return torchsdk_1.TOTAL_SUPPLY; } });
