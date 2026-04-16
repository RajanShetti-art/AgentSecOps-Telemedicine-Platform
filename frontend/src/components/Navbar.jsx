import { Link, useLocation, useNavigate } from "react-router-dom";

export default function Navbar({ onLogout }) {
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    onLogout();
    navigate("/login");
  };

  return (
    <header className="navbar">
      <h2>Telemedicine</h2>
      <nav>
        <Link className={location.pathname === "/dashboard" ? "active" : ""} to="/dashboard">
          Dashboard
        </Link>
        <Link className={location.pathname === "/appointments" ? "active" : ""} to="/appointments">
          Appointments
        </Link>
      </nav>
      <button className="secondary" onClick={handleLogout}>
        Logout
      </button>
    </header>
  );
}
