import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Download, CheckCircle } from 'lucide-react';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import { Badge, getSeverityVariant, getRiskVariant } from '../components/Badge';
import type { ReportSummary, Finding } from '../lib/api';
import { getProjectReport } from '../lib/api';

export const ReportDetail: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [report, setReport] = useState<ReportSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      if (!projectId) return;
      try {
        const res = await getProjectReport(parseInt(projectId));
        setReport(res.data);
      } catch (error) {
        console.error('Error fetching report:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [projectId]);

  const groupedFindings = report?.findings.reduce((acc, f) => {
    if (!acc[f.severity]) acc[f.severity] = [];
    acc[f.severity].push(f);
    return acc;
  }, {} as Record<string, Finding[]>) || {};

  const severityOrder = ['Critical', 'High', 'Medium', 'Low'];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-green-500 font-mono animate-pulse">Loading report...</div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400">Report not found</p>
        <Button variant="outline" className="mt-4" onClick={() => navigate('/app/reports')}>
          Back to Reports
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="flex items-center gap-4">
        <Button variant="ghost" onClick={() => navigate('/app/reports')}>
          <ArrowLeft size={18} />
        </Button>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-mono font-bold text-white">
              Security Report
            </h1>
            {report.overall_risk && (
              <Badge variant={getRiskVariant(report.overall_risk)}>
                {report.overall_risk} Risk
              </Badge>
            )}
          </div>
          <p className="text-gray-400 mt-1">
            {report.project_name} •{' '}
            {report.test_run_date
              ? new Date(report.test_run_date).toLocaleDateString()
              : 'No test date'}
          </p>
        </div>
        <Button variant="secondary" disabled>
          <Download size={18} />
          Download PDF
        </Button>
      </div>

      <Card>
        <h2 className="text-lg font-mono font-semibold text-green-500 mb-4">
          Executive Summary
        </h2>
        <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">
          {report.executive_summary}
        </p>
      </Card>

      <Card>
        <h2 className="text-lg font-mono font-semibold text-green-500 mb-4">
          Key Recommendations
        </h2>
        <div className="space-y-3">
          {report.recommendations.map((rec, i) => (
            <div key={i} className="flex items-start gap-3">
              <CheckCircle size={18} className="text-green-500 mt-0.5 flex-shrink-0" />
              <p className="text-gray-300">{rec}</p>
            </div>
          ))}
        </div>
      </Card>

      <Card>
        <h2 className="text-lg font-mono font-semibold text-green-500 mb-4">
          Vulnerability Summary
        </h2>
        <div className="grid grid-cols-4 gap-4">
          <div className="text-center p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
            <p className="text-2xl font-mono font-bold text-red-400">
              {report.vulnerability_summary.critical}
            </p>
            <p className="text-xs text-gray-400 mt-1">Critical</p>
          </div>
          <div className="text-center p-4 bg-orange-500/10 border border-orange-500/20 rounded-lg">
            <p className="text-2xl font-mono font-bold text-orange-400">
              {report.vulnerability_summary.high}
            </p>
            <p className="text-xs text-gray-400 mt-1">High</p>
          </div>
          <div className="text-center p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
            <p className="text-2xl font-mono font-bold text-yellow-400">
              {report.vulnerability_summary.medium}
            </p>
            <p className="text-xs text-gray-400 mt-1">Medium</p>
          </div>
          <div className="text-center p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
            <p className="text-2xl font-mono font-bold text-green-400">
              {report.vulnerability_summary.low}
            </p>
            <p className="text-xs text-gray-400 mt-1">Low</p>
          </div>
        </div>
      </Card>

      {severityOrder.map((severity) => {
        const findings = groupedFindings[severity];
        if (!findings || findings.length === 0) return null;

        return (
          <Card key={severity}>
            <div className="flex items-center gap-2 mb-4">
              <h2 className="text-lg font-mono font-semibold text-white">
                {severity} Severity Findings
              </h2>
              <Badge variant={getSeverityVariant(severity)}>{findings.length}</Badge>
            </div>

            <div className="space-y-4">
              {findings.map((f) => (
                <div
                  key={f.id}
                  className="bg-[#0a0a0a] border border-[#1a1a1a] rounded-lg p-4"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="font-mono font-semibold text-white">{f.title}</h3>
                    <Badge variant="info">{f.category}</Badge>
                  </div>
                  <p className="text-gray-400 text-sm mb-3">{f.description}</p>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Attack Prompt</p>
                      <div className="bg-black border border-green-500/20 rounded p-2 font-mono text-xs text-green-400 max-h-24 overflow-y-auto">
                        {f.attack_prompt}
                      </div>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 mb-1">Model Response</p>
                      <div className="bg-black border border-[#1a1a1a] rounded p-2 font-mono text-xs text-gray-400 max-h-24 overflow-y-auto">
                        {f.model_response || 'No response'}
                      </div>
                    </div>
                  </div>

                  {f.recommendation && (
                    <div className="mt-3 bg-green-500/5 border border-green-500/10 rounded p-2">
                      <p className="text-xs text-green-400">
                        <strong>Recommendation:</strong> {f.recommendation}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Card>
        );
      })}
    </div>
  );
};
