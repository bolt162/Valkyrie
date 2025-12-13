import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText } from 'lucide-react';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import { Badge, getRiskVariant } from '../components/Badge';
import type { ProjectReport } from '../lib/api';
import { getReports } from '../lib/api';

export const Reports: React.FC = () => {
  const navigate = useNavigate();
  const [reports, setReports] = useState<ProjectReport[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await getReports();
        setReports(res.data);
      } catch (error) {
        console.error('Error fetching reports:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-green-500 font-mono animate-pulse">Loading reports...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-mono font-bold text-white">Reports</h1>
        <p className="text-gray-400 mt-1">Security assessment reports for your projects</p>
      </div>

      {reports.length === 0 ? (
        <Card className="text-center py-12">
          <FileText className="h-12 w-12 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-400">No reports available</p>
          <p className="text-gray-500 text-sm mt-1">
            Run a test on a project to generate a report
          </p>
        </Card>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {reports.map((report) => (
            <Card key={report.project_id} className="hover:border-green-500/30 transition-colors">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
                    <FileText className="h-5 w-5 text-green-500" />
                  </div>
                  <div>
                    <h3 className="font-mono font-semibold text-white">{report.project_name}</h3>
                    <p className="text-gray-500 text-xs">
                      {report.last_test_date
                        ? new Date(report.last_test_date).toLocaleDateString()
                        : 'No tests yet'}
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-gray-500 mb-1">Overall Risk</p>
                  <Badge variant={getRiskVariant(report.overall_risk)}>
                    {report.overall_risk}
                  </Badge>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate(`/app/reports/${report.project_id}`)}
                  disabled={report.overall_risk === 'N/A'}
                >
                  View Report
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
