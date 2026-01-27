import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus } from 'lucide-react';
import { Button } from '../components/Button';
import { Table } from '../components/Table';
import { Modal } from '../components/Modal';
import { Input, Select } from '../components/Input';
import { Badge, getRiskVariant } from '../components/Badge';
import type { Project } from '../lib/api';
import { getProjects, createProject } from '../lib/api';

export const Projects: React.FC = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    model_provider: 'OpenAI',
    connection_type: 'openai-compatible',
    base_url: '',
    model_name: '',
    api_key: '',
    risk_level: 'Medium',
  });

  const fetchProjects = async () => {
    try {
      const res = await getProjects();
      setProjects(res.data);
    } catch (error) {
      console.error('Error fetching projects:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    try {
      await createProject(formData);
      setModalOpen(false);
      setFormData({
        name: '',
        description: '',
        model_provider: 'OpenAI',
        connection_type: 'openai-compatible',
        base_url: '',
        model_name: '',
        api_key: '',
        risk_level: 'Medium',
      });
      fetchProjects();
    } catch (error) {
      console.error('Error creating project:', error);
    } finally {
      setCreating(false);
    }
  };

  const columns = [
    {
      key: 'name',
      header: 'Project Name',
      render: (p: Project) => <span className="font-mono text-gray-900 dark:text-white">{p.name}</span>,
    },
    {
      key: 'model_provider',
      header: 'Provider',
      render: (p: Project) => <span className="text-gray-600 dark:text-gray-400">{p.model_provider}</span>,
    },
    {
      key: 'connection_type',
      header: 'Connection',
      render: (p: Project) => (
        <span className="text-gray-600 dark:text-gray-400 text-xs font-mono">
          {p.connection_type === 'openai-compatible' ? 'OpenAI API' : 'Custom HTTP'}
        </span>
      ),
    },
    {
      key: 'risk_level',
      header: 'Risk Level',
      render: (p: Project) => (
        <Badge variant={getRiskVariant(p.risk_level)}>{p.risk_level}</Badge>
      ),
    },
    {
      key: 'test_run_count',
      header: 'Test Runs',
      render: (p: Project) => (
        <span className="text-gray-600 dark:text-gray-400 font-mono">{p.test_run_count}</span>
      ),
    },
    {
      key: 'last_test_date',
      header: 'Last Test',
      render: (p: Project) => (
        <span className="text-gray-600 dark:text-gray-400 text-sm">
          {p.last_test_date ? new Date(p.last_test_date).toLocaleDateString() : 'Never'}
        </span>
      ),
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-green-600 dark:text-green-500 font-mono animate-pulse">Loading projects...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-mono font-bold text-gray-900 dark:text-white">Projects</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Manage your LLM security testing projects</p>
        </div>
        <Button onClick={() => setModalOpen(true)}>
          <Plus size={18} />
          New Project
        </Button>
      </div>

      <Table
        columns={columns}
        data={projects}
        onRowClick={(p) => navigate(`/app/projects/${p.id}`)}
        emptyMessage="No projects yet. Create your first project to start testing."
      />

      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="New Project"
        size="lg"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Project Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="My LLM Project"
            required
          />

          <Input
            label="Description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="Brief description of the project"
          />

          <div className="grid grid-cols-2 gap-4">
            <Select
              label="Model Provider"
              value={formData.model_provider}
              onChange={(e) => setFormData({ ...formData, model_provider: e.target.value })}
              options={[
                { value: 'OpenAI', label: 'OpenAI' },
                { value: 'Anthropic', label: 'Anthropic' },
                { value: 'Azure OpenAI', label: 'Azure OpenAI' },
                { value: 'Custom', label: 'Custom HTTP' },
              ]}
            />

            <Select
              label="Connection Type"
              value={formData.connection_type}
              onChange={(e) => setFormData({ ...formData, connection_type: e.target.value })}
              options={[
                { value: 'openai-compatible', label: 'OpenAI-compatible' },
                { value: 'custom-http', label: 'Custom HTTP' },
              ]}
            />
          </div>

          <Input
            label="Base URL"
            value={formData.base_url}
            onChange={(e) => setFormData({ ...formData, base_url: e.target.value })}
            placeholder="https://api.openai.com/v1"
          />

          {formData.connection_type === 'openai-compatible' && (
            <Input
              label="Model Name"
              value={formData.model_name}
              onChange={(e) => setFormData({ ...formData, model_name: e.target.value })}
              placeholder="gpt-4"
            />
          )}

          <Input
            label="API Key"
            type="password"
            value={formData.api_key}
            onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
            placeholder="sk-..."
          />

          <Select
            label="Risk Level"
            value={formData.risk_level}
            onChange={(e) => setFormData({ ...formData, risk_level: e.target.value })}
            options={[
              { value: 'Low', label: 'Low' },
              { value: 'Medium', label: 'Medium' },
              { value: 'High', label: 'High' },
            ]}
          />

          <div className="flex justify-end gap-3 pt-4">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setModalOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" loading={creating}>
              Create Project
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
