import axios from 'axios';
import { API_BASE_URL } from '../config/api';

const API_URL = API_BASE_URL;

export interface ApiSecurityTest {
  id: number;
  project_id: number;
  name: string;
  target_url: string;
  auth_type?: string;
  endpoints?: string[];
  test_types?: string[];
  status: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  total_endpoints: number;
  vulnerabilities_found: number;
  log_file?: string;
}

export interface ApiVulnerability {
  id: number;
  api_test_id: number;
  endpoint: string;
  method?: string;
  vulnerability_type: string;
  severity: string;
  title: string;
  description?: string;
  proof_of_concept?: string;
  remediation?: string;
  cvss_score?: number;
  status: string;
  created_at: string;
}

export interface ApiSecurityTestDetail extends ApiSecurityTest {
  vulnerabilities: ApiVulnerability[];
}

export interface CreateApiTestRequest {
  project_id: number;
  name: string;
  target_url: string;
  auth_type?: string;
  auth_credentials?: {
    token?: string;
    key_name?: string;
    key_value?: string;
    username?: string;
    password?: string;
  };
  endpoints: string[];
  test_types: string[];
}

export const apiTestService = {
  // Create a new API security test
  createTest: async (data: CreateApiTestRequest): Promise<ApiSecurityTest> => {
    const response = await axios.post(`${API_URL}/api-tests`, data);
    return response.data;
  },

  // List all API tests
  listTests: async (projectId?: number): Promise<ApiSecurityTest[]> => {
    const params = projectId ? { project_id: projectId } : {};
    const response = await axios.get(`${API_URL}/api-tests`, { params });
    return response.data;
  },

  // Get test details with vulnerabilities
  getTest: async (testId: number): Promise<ApiSecurityTestDetail> => {
    const response = await axios.get(`${API_URL}/api-tests/${testId}`);
    return response.data;
  },

  // Run a test
  runTest: async (testId: number): Promise<{ message: string; test_id: number }> => {
    const response = await axios.post(`${API_URL}/api-tests/${testId}/run`);
    return response.data;
  },

  // Get vulnerabilities for a test
  getVulnerabilities: async (testId: number): Promise<ApiVulnerability[]> => {
    const response = await axios.get(`${API_URL}/api-tests/${testId}/vulnerabilities`);
    return response.data;
  },
};
