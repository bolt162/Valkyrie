import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, AlertTriangle, CheckCircle, XCircle, Clock, Play, Download } from 'lucide-react';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { Modal } from '../components/Modal';
import { apiTestService } from '../services/apiTestService';
import type { ApiSecurityTestDetail, ApiVulnerability } from '../services/apiTestService';
import { API_BASE_URL } from '../config/api';

export const APITestDetail: React.FC = () => {
  const { testId } = useParams<{ testId: string }>();
  const [test, setTest] = useState<ApiSecurityTestDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedVuln, setSelectedVuln] = useState<ApiVulnerability | null>(null);

  useEffect(() => {
    if (testId) {
      loadTest(parseInt(testId));
    }
  }, [testId]);

  const loadTest = async (id: number) => {
    try {
      setLoading(true);
      const data = await apiTestService.getTest(id);
      setTest(data);
    } catch (error) {
      console.error('Failed to load test:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = async () => {
    if (!testId) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api-tests/${testId}/report`);

      if (!response.ok) {
        throw new Error('Failed to download report');
      }

      // Get the blob from the response
      const blob = await response.blob();

      // Create a URL for the blob
      const url = window.URL.createObjectURL(blob);

      // Create a temporary link element and trigger the download
      const link = document.createElement('a');
      link.href = url;
      link.download = `Valkyrie_Security_Report_${test?.name.replace(/ /g, '_')}.pdf`;
      document.body.appendChild(link);
      link.click();

      // Clean up
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading report:', error);
      alert('Failed to download report. Please try again.');
    }
  };

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      critical: 'text-red-500 bg-red-500/10 border-red-500/30',
      high: 'text-orange-500 bg-orange-500/10 border-orange-500/30',
      medium: 'text-yellow-500 bg-yellow-500/10 border-yellow-500/30',
      low: 'text-blue-500 bg-blue-500/10 border-blue-500/30',
    };
    return colors[severity.toLowerCase()] || colors.medium;
  };

  const getStatusIcon = (status: string) => {
    const icons: Record<string, any> = {
      pending: Clock,
      running: Play,
      completed: CheckCircle,
      failed: XCircle,
    };
    const Icon = icons[status] || Clock;
    return <Icon size={20} />;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-600 dark:text-gray-400">Loading test details...</div>
      </div>
    );
  }

  if (!test) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-600 dark:text-gray-400">Test not found</div>
      </div>
    );
  }

  const criticalCount = test.vulnerabilities.filter(v => v.severity === 'critical').length;
  const highCount = test.vulnerabilities.filter(v => v.severity === 'high').length;
  const mediumCount = test.vulnerabilities.filter(v => v.severity === 'medium').length;
  const lowCount = test.vulnerabilities.filter(v => v.severity === 'low').length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <Link
          to="/app/api-testing"
          className="inline-flex items-center gap-2 text-green-600 dark:text-green-500 hover:underline mb-4"
        >
          <ArrowLeft size={18} />
          Back to API Testing
        </Link>

        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-mono font-bold text-gray-900 dark:text-white">{test.name}</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1 font-mono text-sm">{test.target_url}</p>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              {getStatusIcon(test.status)}
              <span className="text-gray-900 dark:text-white capitalize">{test.status}</span>
            </div>

            {test.status === 'completed' && (
              <Button onClick={handleDownloadReport} className="flex items-center gap-2">
                <Download size={18} />
                Download PDF Report
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card>
          <div className="text-center">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Endpoints</p>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">{test.total_endpoints}</p>
          </div>
        </Card>

        <Card>
          <div className="text-center">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Critical</p>
            <p className="text-3xl font-bold text-red-500">{criticalCount}</p>
          </div>
        </Card>

        <Card>
          <div className="text-center">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">High</p>
            <p className="text-3xl font-bold text-orange-500">{highCount}</p>
          </div>
        </Card>

        <Card>
          <div className="text-center">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Medium</p>
            <p className="text-3xl font-bold text-yellow-500">{mediumCount}</p>
          </div>
        </Card>

        <Card>
          <div className="text-center">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Low</p>
            <p className="text-3xl font-bold text-blue-500">{lowCount}</p>
          </div>
        </Card>
      </div>

      {/* Test Details */}
      <Card>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Test Configuration</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Authentication</p>
            <p className="text-gray-900 dark:text-white font-mono">{test.auth_type || 'none'}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400">Created</p>
            <p className="text-gray-900 dark:text-white">{new Date(test.created_at).toLocaleString()}</p>
          </div>
          {test.started_at && (
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Started</p>
              <p className="text-gray-900 dark:text-white">{new Date(test.started_at).toLocaleString()}</p>
            </div>
          )}
          {test.completed_at && (
            <div>
              <p className="text-sm text-gray-600 dark:text-gray-400">Completed</p>
              <p className="text-gray-900 dark:text-white">{new Date(test.completed_at).toLocaleString()}</p>
            </div>
          )}
        </div>

        {test.test_types && test.test_types.length > 0 && (
          <div className="mt-4">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Tests Run</p>
            <div className="flex flex-wrap gap-2">
              {test.test_types.map(type => (
                <span
                  key={type}
                  className="px-3 py-1 rounded-full bg-green-500/10 border border-green-500/30 text-green-600 dark:text-green-500 text-sm font-mono"
                >
                  {type}
                </span>
              ))}
            </div>
          </div>
        )}
      </Card>

      {/* Vulnerabilities */}
      <Card>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Vulnerabilities Found ({test.vulnerabilities.length})
          </h2>
        </div>

        {test.vulnerabilities.length === 0 ? (
          <div className="text-center py-12">
            <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
            <p className="text-gray-900 dark:text-white font-semibold mb-2">No vulnerabilities found!</p>
            <p className="text-gray-600 dark:text-gray-400">Your API passed all security tests.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {test.vulnerabilities.map((vuln) => (
              <div
                key={vuln.id}
                onClick={() => setSelectedVuln(vuln)}
                className="p-4 rounded-lg border border-gray-200 dark:border-[#1a1a1a] hover:border-green-500/30 cursor-pointer transition-colors bg-white dark:bg-[#0a0a0a]"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`px-2 py-1 rounded text-xs font-semibold uppercase border ${getSeverityColor(vuln.severity)}`}>
                        {vuln.severity}
                      </span>
                      <span className="text-xs text-gray-600 dark:text-gray-400 font-mono">
                        {vuln.vulnerability_type}
                      </span>
                      {vuln.cvss_score && (
                        <span className="text-xs text-gray-600 dark:text-gray-400">
                          CVSS: {vuln.cvss_score.toFixed(1)}
                        </span>
                      )}
                    </div>

                    <h3 className="font-semibold text-gray-900 dark:text-white mb-1">{vuln.title}</h3>

                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      {vuln.description}
                    </p>

                    <div className="flex items-center gap-4 text-sm">
                      <span className="text-gray-600 dark:text-gray-400">
                        <span className="font-mono text-xs">{vuln.method || 'GET'}</span>{' '}
                        <span className="font-mono text-green-600 dark:text-green-500">{vuln.endpoint}</span>
                      </span>
                    </div>
                  </div>

                  <AlertTriangle className={vuln.severity === 'critical' ? 'text-red-500' : 'text-orange-500'} />
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Vulnerability Detail Modal */}
      {selectedVuln && (
        <Modal
          isOpen={!!selectedVuln}
          onClose={() => setSelectedVuln(null)}
          title={selectedVuln.title}
          size="xl"
        >
          <div className="space-y-4">
            {/* Severity Badge */}
            <div className="flex items-center gap-2">
              <span className={`px-3 py-1 rounded text-sm font-semibold uppercase border ${getSeverityColor(selectedVuln.severity)}`}>
                {selectedVuln.severity}
              </span>
              {selectedVuln.cvss_score && (
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  CVSS Score: {selectedVuln.cvss_score.toFixed(1)}
                </span>
              )}
            </div>

            {/* Description */}
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Description</h3>
              <p className="text-gray-600 dark:text-gray-400">{selectedVuln.description}</p>
            </div>

            {/* Endpoint */}
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Affected Endpoint</h3>
              <code className="block p-3 bg-gray-100 dark:bg-[#1a1a1a] rounded font-mono text-sm text-gray-900 dark:text-white">
                {selectedVuln.method || 'GET'} {selectedVuln.endpoint}
              </code>
            </div>

            {/* Proof of Concept */}
            {selectedVuln.proof_of_concept && (
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Proof of Concept</h3>
                <pre className="p-3 bg-gray-100 dark:bg-[#1a1a1a] rounded font-mono text-xs text-gray-900 dark:text-white overflow-x-auto">
                  {selectedVuln.proof_of_concept}
                </pre>
              </div>
            )}

            {/* Remediation */}
            {selectedVuln.remediation && (
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Remediation</h3>
                <p className="text-gray-600 dark:text-gray-400">{selectedVuln.remediation}</p>
              </div>
            )}
          </div>
        </Modal>
      )}
    </div>
  );
};
