import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Practice from "./pages/Practice";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/practice" replace />} />
        <Route path="/practice" element={<Practice />} />
        {/* <Route path="/stats" element={<Stats />} /> */}
      </Routes>
    </BrowserRouter>
  );
}
