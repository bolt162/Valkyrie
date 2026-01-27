import axios from 'axios';
import { API_BASE_URL } from '../config/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface DashboardStats {
  total_projects: number;
  total_test_runs: number;
  open_critical_issues: number;
  average_risk_score: string;
}

export interface VulnerabilitySummary {
  critical: number;
  high: number;
  medium: number;
  low: number;
}

export interface Project {
  id: number;
  name: string;
  description: string | null;
  model_provider: string;
  connection_type: string;
  base_url: string | null;
  model_name: string | null;
  risk_level: string;
  created_at: string;
  test_run_count: number;
  last_test_date: string | null;
}

export interface TestRun {
  id: number;
  project_id: number;
  status: string;
  started_at: string;
  finished_at: string | null;
  overall_risk_score: string | null;
  attack_count: number;
  project_name: string | null;
}

export interface Finding {
  id: number;
  test_run_id: number;
  title: string;
  category: string;
  severity: string;
  description: string | null;
  attack_prompt: string;
  model_response: string | null;
  recommendation: string | null;
  created_at: string;
}

export interface TestRunDetail extends TestRun {
  findings: Finding[];
}

export interface ReportSummary {
  project_name: string;
  test_run_date: string | null;
  overall_risk: string | null;
  executive_summary: string;
  recommendations: string[];
  vulnerability_summary: VulnerabilitySummary;
  findings: Finding[];
}

export interface ProjectReport {
  project_id: number;
  project_name: string;
  last_test_date: string | null;
  overall_risk: string;
}

export interface Settings {
  email: string;
  company_name: string;
  timezone: string;
}

export const getDashboardStats = () => api.get<DashboardStats>('/dashboard/stats');
export const getVulnerabilitySummary = () => api.get<VulnerabilitySummary>('/dashboard/vulnerability-summary');
export const getRecentTestRuns = (limit = 10) => api.get<TestRun[]>(`/dashboard/recent-testruns?limit=${limit}`);

export const getProjects = () => api.get<Project[]>('/projects');
export const getProject = (id: number) => api.get<Project>(`/projects/${id}`);
export const createProject = (data: Partial<Project>) => api.post<Project>('/projects', data);
export const getProjectTestRuns = (projectId: number) => api.get<TestRun[]>(`/projects/${projectId}/testruns`);
export const createTestRun = (projectId: number) => api.post<TestRun>(`/projects/${projectId}/testruns`);

export const getTestRun = (id: number) => api.get<TestRunDetail>(`/testruns/${id}`);
export const getTestRunFindings = (id: number) => api.get<Finding[]>(`/testruns/${id}/findings`);

export const getReports = () => api.get<ProjectReport[]>('/reports');
export const getProjectReport = (projectId: number) => api.get<ReportSummary>(`/reports/${projectId}`);

export const getSettings = () => api.get<Settings>('/settings');
export const updateSettings = (data: Partial<Settings>) => api.put('/settings', data);

export default api;
