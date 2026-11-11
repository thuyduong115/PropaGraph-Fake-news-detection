import { Route, Routes } from "react-router-dom";

import Layout from "./components/Layout";
import About from "./pages/About";
import DataReliability from "./pages/DataReliability";
import Explorer from "./pages/Explorer";
import GraphDetail from "./pages/GraphDetail";
import NotFound from "./pages/NotFound";
import Results from "./pages/Results";

// Bảng route khớp DATA_BOUNDARY.md mục 5; đổi route thì cập nhật bảng đó.
export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Explorer />} />
        <Route path="graphs/:ds/:gid" element={<GraphDetail />} />
        <Route path="results" element={<Results />} />
        <Route path="data-reliability" element={<DataReliability />} />
        <Route path="about" element={<About />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}
