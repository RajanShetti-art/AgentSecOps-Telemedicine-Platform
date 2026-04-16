import axios from "axios";

export const authApi = axios.create({
  baseURL: "http://localhost:8000",
});

export const patientApi = axios.create({
  baseURL: "http://localhost:8001",
});

export const appointmentApi = axios.create({
  baseURL: "http://localhost:8002",
});

const attachToken = (config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
};

[authApi, patientApi, appointmentApi].forEach((api) => {
  api.interceptors.request.use(attachToken);
});
