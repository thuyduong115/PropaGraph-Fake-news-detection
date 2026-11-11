import { Route, Routes } from "react-router-dom";

import { RequireAdmin, RequireAuth } from "./auth/guards";
import Layout from "./components/Layout";
import About from "./pages/About";
import Admin from "./pages/Admin";
import DataReliability from "./pages/DataReliability";
import Explorer from "./pages/Explorer";
import GraphDetail from "./pages/GraphDetail";
import Login from "./pages/Login";
import NotFound from "./pages/NotFound";
import Results from "./pages/Results";

// Bảng route khớp DATA_BOUNDARY.md mục 5; đổi route thì cập nhật bảng đó.
export default function App() {
  const guard = (el: JSX.Element) => <RequireAuth>{el}</RequireAuth>;
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="login" element={<Login />} />
        <Route index element={guard(<Explorer />)} />
        <Route path="graphs/:ds/:gid" element={guard(<GraphDetail />)} />
        <Route path="results" element={guard(<Results />)} />
        <Route path="data-reliability" element={guard(<DataReliability />)} />
        <Route path="about" element={guard(<About />)} />
        <Route
          path="admin"
          element={guard(
            <RequireAdmin>
              <Admin />
            </RequireAdmin>,
          )}
        />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}
