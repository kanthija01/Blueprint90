// GET /api/blueprints — list user's blueprints for the dashboard.

import { apiRequest } from "./client";

export type BlueprintListItem = {
  blueprint_id: string;
  created_at: string;
  goal: string;
  primary_module_slug: string;
  primary_module_display_name: string;
  module_count: number;
};

export function listBlueprints(): Promise<BlueprintListItem[]> {
  return apiRequest<BlueprintListItem[]>("/api/blueprints");
}
