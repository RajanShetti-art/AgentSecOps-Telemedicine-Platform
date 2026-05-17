import { useEffect, useState } from "react";
import Spinner from "../components/Spinner";
import Toast from "../components/Toast";
import { createPatient, fetchPatients } from "../services/patientService";

export default function DashboardPage() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [loadError, setLoadError] = useState("");
  const [toast, setToast] = useState({ type: "", message: "" });
  const [fullName, setFullName] = useState("");
  const [illnessDetail, setIllnessDetail] = useState("");

  useEffect(() => {
    if (!toast.message) {
      return undefined;
    }

    const timer = window.setTimeout(() => {
      setToast({ type: "", message: "" });
    }, 3500);

    return () => window.clearTimeout(timer);
  }, [toast]);

  const showToast = (type, message) => {
    setToast({ type, message });
  };

  const loadPatients = async () => {
    setLoading(true);
    setLoadError("");

    try {
      setPatients(await fetchPatients());
    } catch (err) {
      setLoadError("Unable to load patients right now.");
      if (err?.response?.status === 401 || err?.response?.status === 403) {
        showToast("error", "Please sign in again to fetch patients.");
      } else {
        showToast("error", err?.response?.data?.detail || "Failed to fetch patients.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);

    try {
      await createPatient({ fullName, illnessDetail });
      setFullName("");
      setIllnessDetail("");
      await loadPatients();
      showToast("success", "Patient added successfully.");
    } catch (err) {
      if (err?.response?.status === 401 || err?.response?.status === 403) {
        showToast("error", "Please sign in again to add patients.");
      } else {
        showToast("error", err?.response?.data?.detail || "Failed to add patient.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  useEffect(() => {
    loadPatients();
  }, []);

  return (
    <section className="card">
      <Toast type={toast.type} message={toast.message} onClose={() => setToast({ type: "", message: "" })} />

      <div className="row">
        <h1>Patient Dashboard</h1>
        <button className="secondary" onClick={loadPatients}>
          Refresh
        </button>
      </div>

      <form onSubmit={handleSubmit} className="form" style={{ marginBottom: "1.5rem" }}>
        <label htmlFor="patient-name">Patient Name</label>
        <input
          id="patient-name"
          type="text"
          placeholder="Enter patient name"
          value={fullName}
          onChange={(event) => setFullName(event.target.value)}
          minLength={2}
          maxLength={100}
          required
        />

        <label htmlFor="illness-detail">Illness Description</label>
        <textarea
          id="illness-detail"
          placeholder="Describe the illness or symptoms"
          value={illnessDetail}
          onChange={(event) => setIllnessDetail(event.target.value)}
          minLength={2}
          maxLength={200}
          required
          rows={4}
        />

        <button type="submit" disabled={submitting}>
          {submitting ? <Spinner /> : "Add Patient"}
        </button>
      </form>

      {loading ? <Spinner /> : null}

      {!loading && !loadError ? (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Patient Name</th>
              <th>Illness Detail</th>
            </tr>
          </thead>
          <tbody>
            {patients.length === 0 ? (
              <tr>
                <td colSpan="3">No patients found.</td>
              </tr>
            ) : (
              patients.map((patient) => (
                <tr key={patient.id}>
                  <td>{patient.id}</td>
                  <td>{patient.full_name}</td>
                  <td>{patient.condition}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      ) : null}
    </section>
  );
}
