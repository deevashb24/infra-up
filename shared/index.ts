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
    startDate: string;
    endDate: string;
  };
}
