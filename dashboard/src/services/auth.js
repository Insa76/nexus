export function authFetch(url, options = {}) {

  const token = localStorage.getItem("token");

  // 🔴 No hay token → cortar todo
  if (!token) {
    window.location.href = "/login";
    return Promise.reject("No token");
  }

  return fetch(url, {
    ...options,
    headers: {
      ...(options.headers || {}),
      Authorization: `Bearer ${token}`
    }
  })
  .then(res => {

    // 🔴 Token inválido o expirado
    if (res.status === 401) {
      localStorage.clear();
      window.location.href = "/login";
      return Promise.reject("Unauthorized");
    }

    return res;
  });
}

export function getAuthHeaders() {

  const token = localStorage.getItem("token");

  if (!token) {
    throw new Error("No token");
  }

  return {
    Authorization: `Bearer ${token}`
  };
}