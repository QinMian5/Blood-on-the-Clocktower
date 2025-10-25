import "./styles.css";

import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import { JoinPage } from "./pages/JoinPage";
import { RoomPage } from "./pages/RoomPage";

const root = document.getElementById("root");

if (root) {
  ReactDOM.createRoot(root).render(
    <React.StrictMode>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<JoinPage />} />
          <Route path="/room/:roomId" element={<RoomPage />} />
        </Routes>
      </BrowserRouter>
    </React.StrictMode>
  );
}
