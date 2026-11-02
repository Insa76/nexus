import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import Assistant from "./Assistant";
import "./index.css";

const isAssistant = window.location.pathname === "/assistant";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    {isAssistant ? <Assistant /> : <App />}
  </React.StrictMode>,
);