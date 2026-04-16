import { useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import AppointmentsPage from "./pages/AppointmentsPage";
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";

function ProtectedRoute({ token, children }) {
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function App() {
  const [token, setToken] = useState(localStorage.getItem("token") || "");

  const logout = () => {
    localStorage.removeItem("token");
    setToken("");
  };

  return (
    <>
      {token ? <Navbar onLogout={logout} /> : null}
      <main className="container">
        <Routes>
          <Route path="/login" element={<LoginPage onLogin={setToken} />} />
          <Route path="/signup" element={<RegisterPage />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute token={token}>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/appointments"
            element={
              <ProtectedRoute token={token}>
                <AppointmentsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="*"
            element={<Navigate to={token ? "/dashboard" : "/login"} replace />}
          />
        </Routes>
      </main>
    </>
  );
}

export default App;
