import { Routes, Route, Navigate } from "react-router-dom";
import DashboardLayout from "./layouts/DashboardLayout";
import Dashboard from "./pages/Dashboard";
import ProcessManagement from "./pages/ProcessManagement";
import Simulator from "./pages/Simulator";
import Comparison from "./pages/Comparison";
import GanttVisualization from "./pages/GanttVisualization";
import DatasetManagement from "./pages/DatasetManagement";
import ModelTraining from "./pages/ModelTraining";
import Recommendation from "./pages/Recommendation";
import TrainingHistory from "./pages/TrainingHistory";
import About from "./pages/About";

export default function App() {
  return (
    <Routes>
      <Route element={<DashboardLayout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/processes" element={<ProcessManagement />} />
        <Route path="/simulator" element={<Simulator />} />
        <Route path="/comparison" element={<Comparison />} />
        <Route path="/gantt" element={<GanttVisualization />} />
        <Route path="/datasets" element={<DatasetManagement />} />
        <Route path="/training" element={<ModelTraining />} />
        <Route path="/recommendation" element={<Recommendation />} />
        <Route path="/history" element={<TrainingHistory />} />
        <Route path="/about" element={<About />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Route>
    </Routes>
  );
}
