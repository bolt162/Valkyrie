import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Shield, AlertTriangle, CheckCircle } from 'lucide-react';
import { Button } from '../components/Button';
import { Card, StatCard } from '../components/Card';
import { Table } from '../components/Table';
import { Modal } from '../components/Modal';
import { Badge, getSeverityVariant, getStatusVariant, getRiskVariant } from '../components/Badge';
import type { TestRunDetail as TestRunDetailType, Finding } from '../lib/api';
import { getTestRun } from '../lib/api';

export const TestRunDetail: React.FC = () => {
  const { testRunId } = useParams<{ testRunId: string }>();
  const navigate = useNavigate();
  const [testRun, setTestRun] = useState<TestRunDetailType | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!testRunId) return;
      try {
        const res = await getTestRun(parseInt(testRunId));
        setTestRun(res.data);
      } catch (error) {
        console.error('Error fetching test run:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [testRunId]);

  const columns = [
    {
      key: 'title',
      header: 'Attack Title',
      render: (f: Finding) => <span className="font-mono text-white">{f.title}</span>,
    },
    {
      key: 'category',
      header: 'Category',
      render: (f: Finding) => <span className="text-gray-400">{f.category}</span>,
    },
    {
      key: 'severity',
      header: 'Severity',
      render: (f: Finding) => (
        <Badge variant={getSeverityVariant(f.severity)}>{f.severity}</Badge>
      ),
    },
  ];

  const countSeverity = (severity: string) =>
    testRun?.findings.filter((f) => f.severity === severity).length || 0;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-green-500 font-mono animate-pulse">Loading test run...</div>
      </div>
    );
  }

  if (!testRun) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400">Test run not found</p>
        <Button variant="outline" className="mt-4" onClick={() => navigate('/app/dashboard')}>
          Back to Dashboard
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" onClick={() => navigate(-1)}>
          <ArrowLeft size={18} />
        </Button>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-mono font-bold text-white">
              Test Run #{testRun.id}
            </h1>
            <Badge variant={getStatusVariant(testRun.status)}>
              {testRun.status.charAt(0).toUpperCase() + testRun.status.slice(1)}
            </Badge>
            {testRun.overall_risk_score && (
              <Badge variant={getRiskVariant(testRun.overall_risk_score)}>
                {testRun.overall_risk_score} Risk
              </Badge>
            )}
          </div>
          <p className="text-gray-400 mt-1">
            {testRun.project_name} • {new Date(testRun.started_at).toLocaleString()}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          title="Attack Attempts"
          value={testRun.attack_count}
          icon={<Shield size={24} />}
          accentColor="blue"
        />
        <StatCard
          title="Vulnerabilities"
          value={testRun.findings.length}
          icon={<AlertTriangle size={24} />}
          accentColor="red"
        />
        <StatCard
          title="Critical / High"
          value={`${countSeverity('Critical')} / ${countSeverity('High')}`}
          accentColor="red"
        />
        <StatCard
          title="Medium / Low"
          value={`${countSeverity('Medium')} / ${countSeverity('Low')}`}
          accentColor="yellow"
        />
      </div>

      <Card>
        <h2 className="text-lg font-mono font-semibold text-green-500 mb-4">
          Findings
        </h2>
        <Table
          columns={columns}
          data={testRun.findings}
          onRowClick={(f) => setSelectedFinding(f)}
          emptyMessage="No vulnerabilities detected in this test run."
        />
      </Card>

      <Modal
        isOpen={!!selectedFinding}
        onClose={() => setSelectedFinding(null)}
        title={selectedFinding?.title || 'Finding Details'}
        size="xl"
      >
        {selectedFinding && (
          <div className="space-y-4">
            <div className="flex gap-2">
              <Badge variant={getSeverityVariant(selectedFinding.severity)}>
                {selectedFinding.severity}
              </Badge>
              <Badge variant="info">{selectedFinding.category}</Badge>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-gray-400 mb-2">Attack Prompt</h3>
              <div className="bg-[#0a0a0a] border border-green-500/30 rounded-lg p-4 font-mono text-sm text-green-400 whitespace-pre-wrap max-h-40 overflow-y-auto">
                {selectedFinding.attack_prompt}
              </div>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-gray-400 mb-2">Model Response</h3>
              <div className="bg-[#0a0a0a] border border-[#1a1a1a] rounded-lg p-4 font-mono text-sm text-gray-300 whitespace-pre-wrap max-h-40 overflow-y-auto">
                {selectedFinding.model_response || 'No response captured'}
              </div>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-gray-400 mb-2">Description</h3>
              <p className="text-gray-300">{selectedFinding.description || 'No description'}</p>
            </div>

            <div>
              <h3 className="text-sm font-semibold text-gray-400 mb-2">Recommendation</h3>
              <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
                <div className="flex items-start gap-2">
                  <CheckCircle size={18} className="text-green-500 mt-0.5 flex-shrink-0" />
                  <p className="text-gray-300">
                    {selectedFinding.recommendation || 'Review and address this vulnerability.'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};
