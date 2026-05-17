import { patientApi } from "./api";

export async function fetchPatients() {
  const response = await patientApi.get("/patients");
  return Array.isArray(response.data) ? response.data : [];
}

export async function createPatient({ fullName, illnessDetail }) {
  const response = await patientApi.post("/patients", {
    full_name: fullName,
    condition: illnessDetail,
  });
  return response.data;
}
