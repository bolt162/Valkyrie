import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Play, ArrowLeft } from 'lucide-react';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import { Table } from '../components/Table';
import { Badge, getRiskVariant, getStatusVariant } from '../components/Badge';
import type { Project, TestRun } from '../lib/api';
import { getProject, getProjectTestRuns, createTestRun } from '../lib/api';

export const ProjectDetail: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [testRuns, setTestRuns] = useState<TestRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);

  const fetchData = async () => {
    if (!projectId) return;
    try {
      const [projectRes, runsRes] = await Promise.all([
        getProject(parseInt(projectId)),
        getProjectTestRuns(parseInt(projectId)),
      ]);
      setProject(projectRes.data);
      setTestRuns(runsRes.data);
    } catch (error) {
      console.error('Error fetching project:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [projectId]);

  const handleRunTest = async () => {
    if (!projectId) return;
    setRunning(true);
    try {
      const res = await createTestRun(parseInt(projectId));
      navigate(`/app/testruns/${res.data.id}`);
    } catch (error) {
      console.error('Error creating test run:', error);
      setRunning(false);
    }
  };

  const columns = [
    {
      key: 'id',
      header: 'Run ID',
      render: (run: TestRun) => (
        <span className="font-mono text-green-500">#{run.id}</span>
      ),
    },
    {
      key: 'started_at',
      header: 'Start Time',
      render: (run: TestRun) => (
        <span className="text-gray-400">
          {new Date(run.started_at).toLocaleString()}
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (run: TestRun) => (
        <Badge variant={getStatusVariant(run.status)}>
          {run.status.charAt(0).toUpperCase() + run.status.slice(1)}
        </Badge>
      ),
    },
    {
      key: 'overall_risk_score',
      header: 'Risk Score',
      render: (run: TestRun) => (
        <Badge variant={getRiskVariant(run.overall_risk_score || 'N/A')}>
          {run.overall_risk_score || 'N/A'}
        </Badge>
      ),
    },
    {
      key: 'attack_count',
      header: 'Attacks',
      render: (run: TestRun) => (
        <span className="text-gray-400 font-mono">{run.attack_count}</span>
      ),
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-green-500 font-mono animate-pulse">Loading project...</div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400">Project not found</p>
        <Button variant="outline" className="mt-4" onClick={() => navigate('/app/projects')}>
          Back to Projects
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" onClick={() => navigate('/app/projects')}>
          <ArrowLeft size={18} />
        </Button>
        <div className="flex-1">
          <h1 className="text-2xl font-mono font-bold text-white">{project.name}</h1>
          <p className="text-gray-400 mt-1">{project.description || 'No description'}</p>
        </div>
        <Button onClick={handleRunTest} loading={running}>
          <Play size={18} />
          Run New Red-Team Test
        </Button>
      </div>

      <Card>
        <h2 className="text-lg font-mono font-semibold text-green-500 mb-4">
          Project Overview
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-gray-500">Provider</p>
            <p className="text-white font-mono">{project.model_provider}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Connection Type</p>
            <p className="text-white font-mono text-sm">
              {project.connection_type === 'openai-compatible' ? 'OpenAI API' : 'Custom HTTP'}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Base URL</p>
            <p className="text-white font-mono text-sm truncate">
              {project.base_url || 'Not configured'}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Model</p>
            <p className="text-white font-mono">{project.model_name || 'N/A'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Risk Level</p>
            <Badge variant={getRiskVariant(project.risk_level)}>{project.risk_level}</Badge>
          </div>
          <div>
            <p className="text-sm text-gray-500">Created</p>
            <p className="text-gray-400 text-sm">
              {new Date(project.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>
      </Card>

      <Card>
        <h2 className="text-lg font-mono font-semibold text-green-500 mb-4">
          Recent Test Runs
        </h2>
        <Table
          columns={columns}
          data={testRuns}
          onRowClick={(run) => navigate(`/app/testruns/${run.id}`)}
          emptyMessage="No test runs yet. Click 'Run New Red-Team Test' to start."
        />
      </Card>
    </div>
  );
};
