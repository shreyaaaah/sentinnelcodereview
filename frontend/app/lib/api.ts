export function getApiUrl(path: string = ""): string {
  let baseUrl = process.env.NEXT_PUBLIC_API_URL || "";

  if (baseUrl) {
    if (!baseUrl.startsWith("http://") && !baseUrl.startsWith("https://")) {
      baseUrl = `https://${baseUrl}`;
    }
  } else {
    if (typeof window !== "undefined") {
      const hostname = window.location.hostname;
      if (hostname.includes("onrender.com")) {
        // Automatically map frontend service domain (e.g. sentinnelcodereview-frontend.onrender.com)
        // to backend service domain (sentinnelcodereview-backend.onrender.com or sentinel-backend.onrender.com)
        const backendHost = hostname.replace("-frontend", "-backend");
        baseUrl = `https://${backendHost}`;
      } else if (hostname === "localhost" || hostname === "127.0.0.1") {
        baseUrl = "http://localhost:8000";
      } else {
        baseUrl = window.location.origin;
      }
    } else {
      baseUrl = "http://localhost:8000";
    }
  }

  baseUrl = baseUrl.replace(/\/$/, "");
  const cleanPath = path ? (path.startsWith("/") ? path : `/${path}`) : "";
  return `${baseUrl}${cleanPath}`;
}
