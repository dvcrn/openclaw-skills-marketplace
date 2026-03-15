/**
 * Patch for ui/src/ui/app-gateway.ts
 *
 * 1. Add this import at the top:
 *
 *    import { renderTeamProjects } from "./views/team-projects.ts";
 *
 * 2. After `uiPluginRegistry.loadFromGateway(data)`, add:
 *
 *    registerPluginViewRenderers(host as unknown as OpenClawApp);
 *
 * 3. Add this function at the end of the file:
 */

/** Register view renderers for known plugin tabs. */
function registerPluginViewRenderers(host: OpenClawApp): void {
  if (uiPluginRegistry.hasView("team-projects")) {
    uiPluginRegistry.registerViewRenderer("team-projects", () =>
      renderTeamProjects({ client: host.client, connected: host.connected }),
    );
  }
}
