import { authApi } from "./api";

export async function loginWithUsernamePassword(username, password) {
  // Backend expects email + password at /auth/login.
  const response = await authApi.post("/auth/login", {
    email: username,
    password,
  });
  return response.data;
}

export async function registerWithEmailPassword(email, password) {
  const response = await authApi.post("/auth/register", {
    email,
    password,
  });
  return response.data;
}
