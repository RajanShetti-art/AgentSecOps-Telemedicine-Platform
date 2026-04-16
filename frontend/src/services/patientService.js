import { patientApi } from "./api";

export async function fetchPatients() {
  const response = await patientApi.get("/patients");
  return Array.isArray(response.data) ? response.data : [];
}
