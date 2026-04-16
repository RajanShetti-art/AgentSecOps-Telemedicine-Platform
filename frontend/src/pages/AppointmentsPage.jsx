import { useEffect, useState } from "react";
import Spinner from "../components/Spinner";
import {
  createAppointment,
  fetchAppointments,
} from "../services/appointmentService";
import { fetchPatients } from "../services/patientService";

export default function AppointmentsPage() {
  const [patientId, setPatientId] = useState("");
  const [dateTime, setDateTime] = useState("");
  const [doctorName, setDoctorName] = useState("");
  const [reason, setReason] = useState("");
  const [patients, setPatients] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [loadingPatients, setLoadingPatients] = useState(true);
  const [loadingList, setLoadingList] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const loadPatients = async () => {
    setLoadingPatients(true);
    setError("");

    try {
      const patientList = await fetchPatients();
      setPatients(patientList);
      if (!patientId && patientList.length > 0) {
        setPatientId(String(patientList[0].id));
      }
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to fetch patients.");
    } finally {
      setLoadingPatients(false);
    }
  };

  const loadAppointments = async () => {
    setLoadingList(true);
    setError("");

    try {
      setAppointments(await fetchAppointments());
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to fetch appointments.");
    } finally {
      setLoadingList(false);
    }
  };

  useEffect(() => {
    loadPatients();
    loadAppointments();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    setSuccess("");

    try {
      await createAppointment({ patientId, dateTime, doctorName, reason });
      setSuccess("Appointment booked successfully.");
      setPatientId("");
      setDateTime("");
      setDoctorName("");
      setReason("");
      await loadAppointments();
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to create appointment.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className="card">
      <h1>Appointments</h1>

      <form onSubmit={handleSubmit} className="form">
        <label htmlFor="patient-id">Patient</label>
        <select
          id="patient-id"
          value={patientId}
          onChange={(event) => setPatientId(event.target.value)}
          disabled={loadingPatients || patients.length === 0}
          required
        >
          {patients.length === 0 ? (
            <option value="">No patients available</option>
          ) : (
            patients.map((patient) => (
              <option key={patient.id} value={patient.id}>
                {patient.full_name} (ID: {patient.id})
              </option>
            ))
          )}
        </select>

        <label htmlFor="appointment-time">Date and Time</label>
        <input
          id="appointment-time"
          type="datetime-local"
          value={dateTime}
          onChange={(event) => setDateTime(event.target.value)}
          required
        />

        <label htmlFor="doctor-name">Doctor Name</label>
        <input
          id="doctor-name"
          type="text"
          placeholder="Enter doctor name"
          value={doctorName}
          onChange={(event) => setDoctorName(event.target.value)}
          minLength={2}
          maxLength={100}
          required
        />

        <label htmlFor="reason">Reason</label>
        <textarea
          id="reason"
          placeholder="Enter reason for visit"
          value={reason}
          onChange={(event) => setReason(event.target.value)}
          minLength={5}
          maxLength={300}
          required
          rows={4}
        />

        <button
          type="submit"
          disabled={submitting || loadingPatients || patients.length === 0}
        >
          {submitting ? <Spinner /> : "Book Appointment"}
        </button>
      </form>

      {success ? <p className="success">{success}</p> : null}
      {error ? <p className="error">{error}</p> : null}

      <div className="row">
        <h2>Appointment List</h2>
        <button className="secondary" onClick={loadAppointments}>
          Refresh
        </button>
      </div>

      {loadingList ? <Spinner /> : null}

      {!loadingList ? (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Patient ID</th>
              <th>Doctor</th>
              <th>Time</th>
              <th>Reason</th>
            </tr>
          </thead>
          <tbody>
            {appointments.length === 0 ? (
              <tr>
                <td colSpan="5">No appointments found.</td>
              </tr>
            ) : (
              appointments.map((appointment) => (
                <tr key={appointment.id}>
                  <td>{appointment.id}</td>
                  <td>{appointment.patient_id}</td>
                  <td>{appointment.doctor_name}</td>
                  <td>
                    {new Date(appointment.appointment_time).toLocaleString()}
                  </td>
                  <td>{appointment.reason}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      ) : null}
    </section>
  );
}
