import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Shield, Plus, Play, CheckCircle, XCircle, Clock, AlertTriangle } from 'lucide-react';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import { Table } from '../components/Table';
import { Modal } from '../components/Modal';
import { apiTestService } from '../services/apiTestService';
import type { ApiSecurityTest } from '../services/apiTestService';
import { APITestForm } from '../components/APITestForm';

export const APITesting: React.FC = () => {
  const [tests, setTests] = useState<ApiSecurityTest[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [stats, setStats] = useState({
    total: 0,
    critical: 0,
    high: 0,
    running: 0,
  });

  useEffect(() => {
    loadTests();
  }, []);

  const loadTests = async () => {
    try {
      setLoading(true);
      const data = await apiTestService.listTests();
      setTests(data);

      // Calculate stats
      const critical = data.reduce((sum, test) => sum + (test.vulnerabilities_found || 0), 0);
      const running = data.filter(t => t.status === 'running').length;

      setStats({
        total: data.length,
        critical: critical,
        high: critical,
        running: running,
      });
    } catch (error) {
      console.error('Failed to load API tests:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTest = async (testData: any) => {
    try {
      await apiTestService.createTest(testData);
      setIsCreateModalOpen(false);
      loadTests();
    } catch (error) {
      console.error('Failed to create test:', error);
      alert('Failed to create test');
    }
  };

  const handleRunTest = async (testId: number) => {
    try {
      await apiTestService.runTest(testId);
      // Reload tests to show updated status
      setTimeout(() => loadTests(), 1000);
      // Poll for updates every 5 seconds
      const interval = setInterval(() => loadTests(), 5000);
      setTimeout(() => clearInterval(interval), 60000); // Stop after 1 minute
    } catch (error) {
      console.error('Failed to run test:', error);
      alert('Failed to run test');
    }
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, { bg: string; text: string; icon: any }> = {
      pending: { bg: 'bg-gray-500/20', text: 'text-gray-400', icon: Clock },
      running: { bg: 'bg-blue-500/20', text: 'text-blue-400', icon: Play },
      completed: { bg: 'bg-green-500/20', text: 'text-green-400', icon: CheckCircle },
      failed: { bg: 'bg-red-500/20', text: 'text-red-400', icon: XCircle },
    };

    const style = styles[status] || styles.pending;
    const Icon = style.icon;

    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded ${style.bg} ${style.text} text-xs font-mono`}>
        <Icon size={12} />
        {status}
      </span>
    );
  };

  const columns = [
    {
      key: 'name',
      header: 'Test Name',
      render: (test: ApiSecurityTest) => (
        <Link
          to={`/app/api-testing/${test.id}`}
          className="font-mono text-green-600 dark:text-green-500 hover:underline"
        >
          {test.name}
        </Link>
      ),
    },
    {
      key: 'target_url',
      header: 'Target URL',
      render: (test: ApiSecurityTest) => (
        <span className="font-mono text-sm text-gray-600 dark:text-gray-400">
          {test.target_url}
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (test: ApiSecurityTest) => getStatusBadge(test.status),
    },
    {
      key: 'endpoints',
      header: 'Endpoints',
      render: (test: ApiSecurityTest) => (
        <span className="text-gray-900 dark:text-white">{test.total_endpoints}</span>
      ),
    },
    {
      key: 'vulnerabilities',
      header: 'Vulnerabilities',
      render: (test: ApiSecurityTest) => (
        <div className="flex items-center gap-2">
          {test.vulnerabilities_found > 0 ? (
            <>
              <AlertTriangle size={16} className="text-red-500" />
              <span className="font-semibold text-red-500">{test.vulnerabilities_found}</span>
            </>
          ) : (
            <span className="text-gray-500 dark:text-gray-400">0</span>
          )}
        </div>
      ),
    },
    {
      key: 'created_at',
      header: 'Created',
      render: (test: ApiSecurityTest) => (
        <span className="text-sm text-gray-600 dark:text-gray-400">
          {new Date(test.created_at).toLocaleDateString()}
        </span>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (test: ApiSecurityTest) => (
        <div className="flex items-center gap-2">
          {test.status === 'pending' || test.status === 'failed' ? (
            <button
              onClick={() => handleRunTest(test.id)}
              className="px-3 py-1 rounded bg-green-500/10 border border-green-500/30 text-green-600 dark:text-green-500 hover:bg-green-500/20 transition-colors text-sm flex items-center gap-1"
            >
              <Play size={14} />
              Run
            </button>
          ) : test.status === 'running' ? (
            <span className="text-blue-400 text-sm">Running...</span>
          ) : (
            <Link
              to={`/app/api-testing/${test.id}`}
              className="text-green-600 dark:text-green-500 hover:underline text-sm"
            >
              View Results
            </Link>
          )}
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-mono font-bold text-gray-900 dark:text-white">API Security Testing</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Test your APIs for vulnerabilities like JWT flaws, BOLA, and authentication issues
          </p>
        </div>
        <Button onClick={() => setIsCreateModalOpen(true)}>
          <Plus size={18} />
          New API Test
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-lg bg-green-500/10 flex items-center justify-center">
              <Shield className="h-6 w-6 text-green-500" />
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Total Tests</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total}</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-lg bg-red-500/10 flex items-center justify-center">
              <AlertTriangle className="h-6 w-6 text-red-500" />
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Critical Issues</p>
              <p className="text-2xl font-bold text-red-500">{stats.critical}</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-lg bg-orange-500/10 flex items-center justify-center">
              <AlertTriangle className="h-6 w-6 text-orange-500" />
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">High Issues</p>
              <p className="text-2xl font-bold text-orange-500">{stats.high}</p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-lg bg-blue-500/10 flex items-center justify-center">
              <Play className="h-6 w-6 text-blue-500" />
            </div>
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Running Tests</p>
              <p className="text-2xl font-bold text-blue-500">{stats.running}</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Tests Table */}
      <Card>
        <div className="mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Recent API Tests</h2>
        </div>

        {loading ? (
          <div className="text-center py-12 text-gray-600 dark:text-gray-400">Loading tests...</div>
        ) : tests.length === 0 ? (
          <div className="text-center py-12">
            <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400 mb-4">No API tests yet</p>
            <Button onClick={() => setIsCreateModalOpen(true)}>
              <Plus size={18} />
              Create Your First API Test
            </Button>
          </div>
        ) : (
          <Table columns={columns} data={tests} />
        )}
      </Card>

      {/* Create Test Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Create API Security Test"
        size="lg"
      >
        <APITestForm onSubmit={handleCreateTest} onCancel={() => setIsCreateModalOpen(false)} />
      </Modal>
    </div>
  );
};
