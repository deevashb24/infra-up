// Shared types and constants for the Civic Tech Platform

export interface PermitFeature {
  type: "Feature";
  geometry: {
    type: "Point" | "Polygon";
    coordinates: number[] | number[][][];
  };
  properties: {
    id: string;
    title: string;
    permitType: "CONSTRUCTION" | "ROAD" | "UTILITY";
    status: "PENDING" | "ACTIVE" | "COMPLETED";
    project_authority: string;
    contractor: string;
    district: string;
    division: string;
    impactLevel: "LOW" | "MEDIUM" | "HIGH";
    budget: number;
    completion_percent: number;
    startDate: string;
    endDate: string;
    is_verified: boolean;
  };
}

export interface DashboardStats {
  total_projects: number;
  active_projects: number;
  delayed_count: number;
  total_budget: number;
  total_reports: number;
  by_type: { name: string; value: number }[];
  by_authority: { name: string; Active: number; Delayed: number }[];
}
