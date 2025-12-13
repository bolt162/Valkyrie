import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FolderKanban, Play, AlertTriangle, TrendingUp } from 'lucide-react';
import { StatCard, Card } from '../components/Card';
import { Table } from '../components/Table';
import { Badge, getStatusVariant, getRiskVariant } from '../components/Badge';
import type { DashboardStats, VulnerabilitySummary, TestRun } from '../lib/api';
import { getDashboardStats, getVulnerabilitySummary, getRecentTestRuns } from '../lib/api';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [vulnSummary, setVulnSummary] = useState<VulnerabilitySummary | null>(null);
  const [recentRuns, setRecentRuns] = useState<TestRun[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, vulnRes, runsRes] = await Promise.all([
          getDashboardStats(),
          getVulnerabilitySummary(),
          getRecentTestRuns(5),
        ]);
        setStats(statsRes.data);
        setVulnSummary(vulnRes.data);
        setRecentRuns(runsRes.data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const columns = [
    {
      key: 'project_name',
      header: 'Project',
      render: (run: TestRun) => (
        <span className="font-mono text-white">{run.project_name || 'Unknown'}</span>
      ),
    },
    {
      key: 'started_at',
      header: 'Run Date',
      render: (run: TestRun) => (
        <span className="text-gray-400">
          {new Date(run.started_at).toLocaleDateString()}
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
      header: 'Risk',
      render: (run: TestRun) => (
        <Badge variant={getRiskVariant(run.overall_risk_score || 'N/A')}>
          {run.overall_risk_score || 'N/A'}
        </Badge>
      ),
    },
  ];

  const maxVuln = vulnSummary
    ? Math.max(vulnSummary.critical, vulnSummary.high, vulnSummary.medium, vulnSummary.low, 1)
    : 1;

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
        <h1 className="text-2xl font-mono font-bold text-white">Dashboard</h1>
        <p className="text-gray-400 mt-1">Security overview and recent activity</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Projects"
          value={stats?.total_projects || 0}
          icon={<FolderKanban size={24} />}
          accentColor="green"
        />
        <StatCard
          title="Total Test Runs"
          value={stats?.total_test_runs || 0}
          icon={<Play size={24} />}
          accentColor="blue"
        />
        <StatCard
          title="Critical Issues"
          value={stats?.open_critical_issues || 0}
          icon={<AlertTriangle size={24} />}
          accentColor="red"
        />
        <StatCard
          title="Avg Risk Score"
          value={stats?.average_risk_score || 'N/A'}
          icon={<TrendingUp size={24} />}
          accentColor="yellow"
        />
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card>
            <h2 className="text-lg font-mono font-semibold text-green-500 mb-4">
              Recent Test Runs
            </h2>
            <Table
              columns={columns}
              data={recentRuns}
              onRowClick={(run) => navigate(`/app/testruns/${run.id}`)}
              emptyMessage="No test runs yet. Create a project to get started."
            />
          </Card>
        </div>

        <div>
          <Card>
            <h2 className="text-lg font-mono font-semibold text-green-500 mb-4">
              Vulnerabilities by Severity
            </h2>
            <div className="space-y-3">
              {vulnSummary && (
                <>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-red-400">Critical</span>
                      <span className="text-gray-400 font-mono">{vulnSummary.critical}</span>
                    </div>
                    <div className="h-3 bg-[#1a1a1a] rounded-full overflow-hidden">
                      <div
                        className="h-full bg-red-500 rounded-full transition-all duration-500"
                        style={{ width: `${(vulnSummary.critical / maxVuln) * 100}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-orange-400">High</span>
                      <span className="text-gray-400 font-mono">{vulnSummary.high}</span>
                    </div>
                    <div className="h-3 bg-[#1a1a1a] rounded-full overflow-hidden">
                      <div
                        className="h-full bg-orange-500 rounded-full transition-all duration-500"
                        style={{ width: `${(vulnSummary.high / maxVuln) * 100}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-yellow-400">Medium</span>
                      <span className="text-gray-400 font-mono">{vulnSummary.medium}</span>
                    </div>
                    <div className="h-3 bg-[#1a1a1a] rounded-full overflow-hidden">
                      <div
                        className="h-full bg-yellow-500 rounded-full transition-all duration-500"
                        style={{ width: `${(vulnSummary.medium / maxVuln) * 100}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-green-400">Low</span>
                      <span className="text-gray-400 font-mono">{vulnSummary.low}</span>
                    </div>
                    <div className="h-3 bg-[#1a1a1a] rounded-full overflow-hidden">
                      <div
                        className="h-full bg-green-500 rounded-full transition-all duration-500"
                        style={{ width: `${(vulnSummary.low / maxVuln) * 100}%` }}
                      />
                    </div>
                  </div>
                </>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
