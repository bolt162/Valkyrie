import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Play, AlertTriangle, TrendingUp, CheckCircle, XCircle, Clock } from 'lucide-react';
import { StatCard, Card } from '../components/Card';
import { Table } from '../components/Table';
import { Badge } from '../components/Badge';
import { apiTestService } from '../services/apiTestService';
import type { ApiSecurityTest } from '../services/apiTestService';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [tests, setTests] = useState<ApiSecurityTest[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalTests: 0,
    totalVulnerabilities: 0,
    criticalIssues: 0,
    runningTests: 0,
  });
  const [vulnSummary, setVulnSummary] = useState({
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
  });

  const fetchData = async (showLoading = true) => {
    try {
      if (showLoading) setLoading(true);
      const data = await apiTestService.listTests();
      setTests(data);

      // Calculate stats from API tests
      const totalVulns = data.reduce((sum, test) => sum + (test.vulnerabilities_found || 0), 0);
      const running = data.filter(t => t.status === 'running').length;

      setStats({
        totalTests: data.length,
        totalVulnerabilities: totalVulns,
        criticalIssues: totalVulns, // Will be refined when we have severity breakdown
        runningTests: running,
      });

      // Calculate vulnerability summary from completed tests with vulnerabilities
      const completedWithVulns = data.filter(t => t.status === 'completed' && t.vulnerabilities_found > 0);
      let critical = 0, high = 0, medium = 0, low = 0;

      for (const test of completedWithVulns) {
        try {
          const vulns = await apiTestService.getVulnerabilities(test.id);
          for (const v of vulns) {
            switch (v.severity?.toLowerCase()) {
              case 'critical': critical++; break;
              case 'high': high++; break;
              case 'medium': medium++; break;
              case 'low': low++; break;
            }
          }
        } catch {
          // Skip if we can't fetch vulns for this test
        }
      }

      setVulnSummary({ critical, high, medium, low });
      setStats(prev => ({ ...prev, criticalIssues: critical }));
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Poll every 5s unconditionally — avoids stale closure bugs
  useEffect(() => {
    fetchData(true);
    const interval = setInterval(() => fetchData(false), 5000);
    return () => clearInterval(interval);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

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
        <span
          className="font-mono text-green-600 dark:text-green-500 cursor-pointer hover:underline"
          onClick={() => navigate(`/app/api-testing/${test.id}`)}
        >
          {test.name}
        </span>
      ),
    },
    {
      key: 'target_url',
      header: 'Target',
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
      key: 'vulnerabilities',
      header: 'Vulnerabilities',
      render: (test: ApiSecurityTest) => (
        <div className="flex items-center gap-2">
          {test.vulnerabilities_found > 0 ? (
            <>
              <AlertTriangle size={14} className="text-red-500" />
              <span className="font-semibold text-red-500">{test.vulnerabilities_found}</span>
            </>
          ) : test.status === 'completed' ? (
            <span className="text-green-500">0</span>
          ) : (
            <span className="text-gray-500 dark:text-gray-400">—</span>
          )}
        </div>
      ),
    },
  ];

  const maxVuln = Math.max(vulnSummary.critical, vulnSummary.high, vulnSummary.medium, vulnSummary.low, 1);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-green-500 font-mono animate-pulse">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-mono font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">Security overview and recent activity</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Tests"
          value={stats.totalTests}
          icon={<Shield size={24} />}
          accentColor="green"
        />
        <StatCard
          title="Vulnerabilities Found"
          value={stats.totalVulnerabilities}
          icon={<AlertTriangle size={24} />}
          accentColor="red"
        />
        <StatCard
          title="Critical Issues"
          value={stats.criticalIssues}
          icon={<AlertTriangle size={24} />}
          accentColor="yellow"
        />
        <StatCard
          title="Running Tests"
          value={stats.runningTests}
          icon={<Play size={24} />}
          accentColor="blue"
        />
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card>
            <h2 className="text-lg font-mono font-semibold text-green-600 dark:text-green-500 mb-4">
              Recent Tests
            </h2>
            <Table
              columns={columns}
              data={tests.slice(0, 5)}
              onRowClick={(test) => navigate(`/app/api-testing/${test.id}`)}
              emptyMessage="No tests yet. Create a test to get started."
            />
          </Card>
        </div>

        <div>
          <Card>
            <h2 className="text-lg font-mono font-semibold text-green-600 dark:text-green-500 mb-4">
              Vulnerabilities by Severity
            </h2>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-red-500 dark:text-red-400">Critical</span>
                  <span className="text-gray-600 dark:text-gray-400 font-mono">{vulnSummary.critical}</span>
                </div>
                <div className="h-3 bg-gray-200 dark:bg-[#1a1a1a] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-red-500 rounded-full transition-all duration-500"
                    style={{ width: `${(vulnSummary.critical / maxVuln) * 100}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-orange-500 dark:text-orange-400">High</span>
                  <span className="text-gray-600 dark:text-gray-400 font-mono">{vulnSummary.high}</span>
                </div>
                <div className="h-3 bg-gray-200 dark:bg-[#1a1a1a] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-orange-500 rounded-full transition-all duration-500"
                    style={{ width: `${(vulnSummary.high / maxVuln) * 100}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-yellow-500 dark:text-yellow-400">Medium</span>
                  <span className="text-gray-600 dark:text-gray-400 font-mono">{vulnSummary.medium}</span>
                </div>
                <div className="h-3 bg-gray-200 dark:bg-[#1a1a1a] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-yellow-500 rounded-full transition-all duration-500"
                    style={{ width: `${(vulnSummary.medium / maxVuln) * 100}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-green-500 dark:text-green-400">Low</span>
                  <span className="text-gray-600 dark:text-gray-400 font-mono">{vulnSummary.low}</span>
                </div>
                <div className="h-3 bg-gray-200 dark:bg-[#1a1a1a] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-green-500 rounded-full transition-all duration-500"
                    style={{ width: `${(vulnSummary.low / maxVuln) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
