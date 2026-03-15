/**
 * Patch for ui/src/ui/app-render.ts
 *
 * 1. Add these imports at the top:
 *
 *    import { uiPluginRegistry } from "./plugins/registry.ts";
 *    import { isPluginTab, getPluginViewInfo } from "./navigation.ts";
 *
 * 2. Before </main>, add:
 *
 *    ${renderPluginTabContent(state)}
 *
 * 3. Add this function (before renderCompactionSettingsView or similar):
 */

// Add this function to app-render.ts:

function renderPluginTabContent(state: AppViewState) {
  if (!isPluginTab(state.tab)) return nothing;
  const view = getPluginViewInfo(state.tab);
  if (!view) return nothing;

  // Check if a custom renderer is registered
  const renderer = uiPluginRegistry.getViewRenderer(state.tab);
  if (renderer) return renderer();

  // Default: show a placeholder with the plugin info
  return html`
    <div class="plugin-view" style="padding: 24px;">
      <div
        style="background: var(--bg-secondary, #1a1a2e); border: 1px solid var(--border, #333); border-radius: 12px; padding: 32px; text-align: center;"
      >
        <div style="font-size: 48px; margin-bottom: 16px;">📋</div>
        <h2 style="margin: 0 0 8px 0; font-size: 20px;">${view.label}</h2>
        <p style="color: var(--text-muted, #888); margin: 0 0 24px 0;">${view.subtitle || ""}</p>
        <p style="color: var(--text-muted, #666); font-size: 13px;">
          Plugin view registered by <code>${view.pluginId || "unknown"}</code>
        </p>
      </div>
    </div>
  `;
}
