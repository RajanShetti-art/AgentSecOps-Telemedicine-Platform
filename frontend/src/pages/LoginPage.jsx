import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import Spinner from "../components/Spinner";
import { loginWithUsernamePassword } from "../services/authService";

export default function LoginPage({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const message = location.state?.message || "";

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const data = await loginWithUsernamePassword(username, password);
      localStorage.setItem("token", data.access_token);
      onLogin(data.access_token);
      navigate("/dashboard");
    } catch (err) {
      setError(
        err?.response?.data?.detail || "Login failed. Check credentials.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card auth-card">
      <h1>Login</h1>
      <form onSubmit={handleSubmit} className="form">
        <label htmlFor="username">Email</label>
        <input
          id="username"
          type="email"
          placeholder="Enter email"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
          required
        />

        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          placeholder="Enter password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
        />

        {error ? <p className="error">{error}</p> : null}
        {message ? <p className="success">{message}</p> : null}

        <button type="submit" disabled={loading}>
          {loading ? <Spinner /> : "Login"}
        </button>
      </form>

      <p className="auth-footer">
        Need an account? <Link to="/signup">Sign up</Link>
      </p>
    </section>
  );
}
