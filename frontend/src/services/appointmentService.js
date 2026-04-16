import { appointmentApi } from "./api";

export async function fetchAppointments() {
  const response = await appointmentApi.get("/appointments");
  return Array.isArray(response.data) ? response.data : [];
}

export async function createAppointment({
  patientId,
  dateTime,
  doctorName,
  reason,
}) {
  const payload = {
    patient_id: Number(patientId),
    appointment_time: new Date(dateTime).toISOString(),
    doctor_name: doctorName,
    reason,
  };

  const response = await appointmentApi.post("/appointments", payload);
  return response.data;
}
