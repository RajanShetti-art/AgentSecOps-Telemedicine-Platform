import { useEffect, useState } from "react";
import Spinner from "../components/Spinner";
import { fetchPatients } from "../services/patientService";

export default function DashboardPage() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadPatients = async () => {
    setLoading(true);
    setError("");

    try {
      setPatients(await fetchPatients());
    } catch (err) {
      setError(err?.response?.data?.detail || "Failed to fetch patients.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPatients();
  }, []);

  return (
    <section className="card">
      <div className="row">
        <h1>Patient Dashboard</h1>
        <button className="secondary" onClick={loadPatients}>
          Refresh
        </button>
      </div>

      {loading ? <Spinner /> : null}
      {error ? <p className="error">{error}</p> : null}

      {!loading && !error ? (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Full Name</th>
              <th>Age</th>
              <th>Condition</th>
            </tr>
          </thead>
          <tbody>
            {patients.length === 0 ? (
              <tr>
                <td colSpan="4">No patients found.</td>
              </tr>
            ) : (
              patients.map((patient) => (
                <tr key={patient.id}>
                  <td>{patient.id}</td>
                  <td>{patient.full_name}</td>
                  <td>{patient.age}</td>
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
