import React, { useState, useEffect } from 'react';
import { Plus, X } from 'lucide-react';
import { Button } from './Button';
import { Input } from './Input';
import axios from 'axios';
import { API_BASE_URL } from '../config/api';

interface Project {
  id: number;
  name: string;
}

interface APITestFormProps {
  onSubmit: (data: any) => void;
  onCancel: () => void;
}

export const APITestForm: React.FC<APITestFormProps> = ({ onSubmit, onCancel }) => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [discovering, setDiscovering] = useState(false);
  const [discoveryResults, setDiscoveryResults] = useState<any>(null);
  const [formData, setFormData] = useState({
    project_id: 0,
    name: '',
    target_url: '',
    auth_type: 'none',
    auth_credentials: {
      token: '',
      key_name: 'X-API-Key',
      key_value: '',
      username: '',
      password: '',
    },
    endpoints: [''],
    test_types: ['sqli', 'xss', 'auth', 'rate_limit'],
  });

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/projects`);
      setProjects(response.data);
      if (response.data.length > 0) {
        setFormData(prev => ({ ...prev, project_id: response.data[0].id }));
      }
    } catch (error) {
      console.error('Failed to load projects:', error);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Filter out empty endpoints
    const endpoints = formData.endpoints.filter(ep => ep.trim() !== '');

    if (endpoints.length === 0) {
      alert('Please add at least one endpoint');
      return;
    }

    onSubmit({
      ...formData,
      endpoints,
    });
  };

  const addEndpoint = () => {
    setFormData(prev => ({
      ...prev,
      endpoints: [...prev.endpoints, ''],
    }));
  };

  const removeEndpoint = (index: number) => {
    setFormData(prev => ({
      ...prev,
      endpoints: prev.endpoints.filter((_, i) => i !== index),
    }));
  };

  const updateEndpoint = (index: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      endpoints: prev.endpoints.map((ep, i) => (i === index ? value : ep)),
    }));
  };

  const toggleTestType = (type: string) => {
    setFormData(prev => ({
      ...prev,
      test_types: prev.test_types.includes(type)
        ? prev.test_types.filter(t => t !== type)
        : [...prev.test_types, type],
    }));
  };

  const handleDiscoverEndpoints = async () => {
    if (!formData.target_url) {
      alert('Please enter a target URL first');
      return;
    }

    setDiscovering(true);
    setDiscoveryResults(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/api-discovery/discover`, {
        target_url: formData.target_url,
      });

      if (response.data.success) {
        const discoveries = response.data.discoveries;
        setDiscoveryResults(discoveries);

        // Auto-populate endpoints
        if (discoveries.endpoints && discoveries.endpoints.length > 0) {
          setFormData(prev => ({
            ...prev,
            endpoints: discoveries.endpoints,
          }));
        }

        alert(`✓ Discovery complete!\n\nFound:\n- ${discoveries.endpoints?.length || 0} endpoints\n- ${discoveries.subdomains?.length || 0} subdomains\n- ${Object.keys(discoveries.technologies || {}).length} technologies`);
      } else {
        alert(`Discovery failed: ${response.data.error}`);
      }
    } catch (error) {
      console.error('Discovery error:', error);
      alert('Failed to discover endpoints. Check console for details.');
    } finally {
      setDiscovering(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Project Selection — hidden for hackathon, auto-selects first project */}
      {/* <div>
        <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
          Project
        </label>
        <select
          value={formData.project_id}
          onChange={(e) => setFormData(prev => ({ ...prev, project_id: parseInt(e.target.value) }))}
          className="w-full px-3 py-2 border border-gray-200 dark:border-[#1a1a1a] rounded-lg bg-white dark:bg-[#0a0a0a] text-gray-900 dark:text-white focus:outline-none focus:border-green-500 transition-colors"
          required
        >
          {projects.map(project => (
            <option key={project.id} value={project.id}>
              {project.name}
            </option>
          ))}
        </select>
      </div> */}

      {/* Test Name */}
      <Input
        label="Test Name"
        value={formData.name}
        onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
        placeholder="e.g., Production API Security Test"
        required
      />

      {/* Target URL */}
      <div>
        <Input
          label="Target URL"
          value={formData.target_url}
          onChange={(e) => setFormData(prev => ({ ...prev, target_url: e.target.value }))}
          placeholder="https://api.example.com"
          required
        />
        <button
          type="button"
          onClick={handleDiscoverEndpoints}
          disabled={discovering || !formData.target_url}
          className="mt-2 w-full px-4 py-2 rounded-lg border border-green-500/30 bg-green-500/10 text-green-600 dark:text-green-500 hover:bg-green-500/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {discovering ? (
            <>
              <div className="w-4 h-4 border-2 border-green-500 border-t-transparent rounded-full animate-spin"></div>
              Discovering endpoints...
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              Auto-Discover Endpoints (AI-Powered)
            </>
          )}
        </button>

        {/* Discovery Results Summary */}
        {discoveryResults && (
          <div className="mt-3 p-3 rounded-lg bg-green-500/5 border border-green-500/20 text-sm">
            <div className="font-semibold text-green-600 dark:text-green-500 mb-2">Discovery Results:</div>
            <div className="space-y-1 text-gray-600 dark:text-gray-400">
              <div>✓ {discoveryResults.endpoints?.length || 0} API endpoints found</div>
              <div>✓ {discoveryResults.subdomains?.length || 0} subdomains discovered</div>
              <div>✓ {Object.keys(discoveryResults.technologies || {}).length} technologies detected</div>
              {discoveryResults.api_documentation?.length > 0 && (
                <div>✓ {discoveryResults.api_documentation.length} API documentation pages found</div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Authentication Type */}
      <div>
        <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
          Authentication Type
        </label>
        <select
          value={formData.auth_type}
          onChange={(e) => setFormData(prev => ({ ...prev, auth_type: e.target.value }))}
          className="w-full px-3 py-2 border border-gray-200 dark:border-[#1a1a1a] rounded-lg bg-white dark:bg-[#0a0a0a] text-gray-900 dark:text-white focus:outline-none focus:border-green-500 transition-colors"
        >
          <option value="none">None</option>
          <option value="bearer">Bearer Token (JWT)</option>
          <option value="api_key">API Key</option>
          <option value="basic">Basic Auth</option>
        </select>
      </div>

      {/* Authentication Credentials */}
      {formData.auth_type === 'bearer' && (
        <Input
          label="Bearer Token"
          value={formData.auth_credentials.token}
          onChange={(e) => setFormData(prev => ({
            ...prev,
            auth_credentials: { ...prev.auth_credentials, token: e.target.value },
          }))}
          placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        />
      )}

      {formData.auth_type === 'api_key' && (
        <>
          <Input
            label="API Key Header Name"
            value={formData.auth_credentials.key_name}
            onChange={(e) => setFormData(prev => ({
              ...prev,
              auth_credentials: { ...prev.auth_credentials, key_name: e.target.value },
            }))}
            placeholder="X-API-Key"
          />
          <Input
            label="API Key Value"
            value={formData.auth_credentials.key_value}
            onChange={(e) => setFormData(prev => ({
              ...prev,
              auth_credentials: { ...prev.auth_credentials, key_value: e.target.value },
            }))}
            placeholder="your-api-key-here"
          />
        </>
      )}

      {formData.auth_type === 'basic' && (
        <>
          <Input
            label="Username"
            value={formData.auth_credentials.username}
            onChange={(e) => setFormData(prev => ({
              ...prev,
              auth_credentials: { ...prev.auth_credentials, username: e.target.value },
            }))}
            placeholder="admin"
          />
          <Input
            label="Password"
            type="password"
            value={formData.auth_credentials.password}
            onChange={(e) => setFormData(prev => ({
              ...prev,
              auth_credentials: { ...prev.auth_credentials, password: e.target.value },
            }))}
            placeholder="••••••••"
          />
        </>
      )}

      {/* Endpoints */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="block text-sm font-medium text-gray-900 dark:text-white">
            Endpoints to Test
          </label>
          <button
            type="button"
            onClick={addEndpoint}
            className="text-sm text-green-600 dark:text-green-500 hover:text-green-500 dark:hover:text-green-400 flex items-center gap-1"
          >
            <Plus size={14} />
            Add Endpoint
          </button>
        </div>

        <div className="space-y-2">
          {formData.endpoints.map((endpoint, index) => (
            <div key={index} className="flex items-center gap-2">
              <input
                type="text"
                value={endpoint}
                onChange={(e) => updateEndpoint(index, e.target.value)}
                placeholder="/api/users/123"
                className="flex-1 px-3 py-2 border border-gray-200 dark:border-[#1a1a1a] rounded-lg bg-white dark:bg-[#0a0a0a] text-gray-900 dark:text-white focus:outline-none focus:border-green-500 transition-colors font-mono text-sm"
              />
              {formData.endpoints.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeEndpoint(index)}
                  className="p-2 text-gray-400 hover:text-red-500 transition-colors"
                >
                  <X size={18} />
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Test Types */}
      <div>
        <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
          Security Tests to Run
        </label>
        <div className="space-y-2">
          {[
            { value: 'sqli', label: 'SQL Injection', desc: 'Login bypass, search injection, error-based and union-based detection' },
            { value: 'xss', label: 'XSS Testing (rtrvr.ai)', desc: 'Cross-site scripting detection using real browser DOM execution' },
            { value: 'auth', label: 'Authentication', desc: 'Missing auth, invalid tokens' },
            { value: 'rate_limit', label: 'Rate Limiting', desc: 'DoS protection' },
            // { value: 'unauth', label: 'Unauthenticated Tests', desc: 'Security headers, CORS, exposed files, cookies' },
            // { value: 'fuzzing', label: 'Smart Fuzzing & Discovery', desc: 'Directory fuzzing, admin panels, cloud storage, backup files' },
            // { value: 'ai_testing', label: 'AI-Powered Smart Testing', desc: 'Endpoint prediction, behavioral analysis, context-aware payloads' },
            // { value: 'network', label: 'Network-Level Testing', desc: 'Port scanning, service detection, WAF/CDN identification, SSL/TLS analysis' },
            // { value: 'jwt', label: 'JWT Vulnerabilities', desc: 'None algorithm, weak secrets, missing expiration' },
            // { value: 'bola', label: 'BOLA/IDOR', desc: 'Broken Object Level Authorization' },
            // { value: 'mass_assignment', label: 'Mass Assignment', desc: 'Unauthorized field modification' },
          ].map(test => (
            <label
              key={test.value}
              className="flex items-start gap-3 p-3 rounded-lg border border-gray-200 dark:border-[#1a1a1a] bg-white dark:bg-[#0a0a0a] cursor-pointer hover:border-green-500/30 transition-colors"
            >
              <input
                type="checkbox"
                checked={formData.test_types.includes(test.value)}
                onChange={() => toggleTestType(test.value)}
                className="mt-1 rounded border-gray-300 text-green-500 focus:ring-green-500"
              />
              <div className="flex-1">
                <div className="font-medium text-gray-900 dark:text-white">{test.label}</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">{test.desc}</div>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Form Actions */}
      <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200 dark:border-[#1a1a1a]">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit">
          Create Test
        </Button>
      </div>
    </form>
  );
};
