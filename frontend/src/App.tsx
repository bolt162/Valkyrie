import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { AppLayout } from './layouts/AppLayout';
import { Landing } from './pages/Landing';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Projects } from './pages/Projects';
import { ProjectDetail } from './pages/ProjectDetail';
import { TestRunDetail } from './pages/TestRunDetail';
import { Reports } from './pages/Reports';
import { ReportDetail } from './pages/ReportDetail';
import { Settings } from './pages/Settings';
import { APITesting } from './pages/APITesting';
import { APITestDetail } from './pages/APITestDetail';
import { Monitoring } from './pages/Monitoring';

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/app" element={<AppLayout />}>
            <Route index element={<Navigate to="/app/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="projects" element={<Projects />} />
            <Route path="projects/:projectId" element={<ProjectDetail />} />
            <Route path="testruns/:testRunId" element={<TestRunDetail />} />
            <Route path="api-testing" element={<APITesting />} />
            <Route path="api-testing/:testId" element={<APITestDetail />} />
            <Route path="monitoring" element={<Monitoring />} />
            <Route path="reports" element={<Reports />} />
            <Route path="reports/:projectId" element={<ReportDetail />} />
            <Route path="settings" element={<Settings />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
