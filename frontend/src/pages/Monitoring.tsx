import React from 'react';
import { Activity } from 'lucide-react';
import { Card } from '../components/Card';

export const Monitoring: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-mono font-bold text-gray-900 dark:text-white">Continuous Monitoring</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          24/7 monitoring for your APIs and infrastructure
        </p>
      </div>

      <Card>
        <div className="text-center py-12">
          <Activity className="h-16 w-16 text-green-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Coming Soon</h2>
          <p className="text-gray-600 dark:text-gray-400 max-w-md mx-auto">
            Continuous monitoring features are currently being built. You'll be able to set up 24/7 monitoring
            for API health, LLM prompts, and infrastructure changes.
          </p>
        </div>
      </Card>
    </div>
  );
};
