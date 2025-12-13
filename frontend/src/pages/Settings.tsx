import React, { useEffect, useState } from 'react';
import { Check } from 'lucide-react';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import { Input, Select } from '../components/Input';
import type { Settings as SettingsType } from '../lib/api';
import { getSettings, updateSettings } from '../lib/api';

const timezones = [
  { value: 'UTC', label: 'UTC' },
  { value: 'America/New_York', label: 'Eastern Time (US)' },
  { value: 'America/Chicago', label: 'Central Time (US)' },
  { value: 'America/Denver', label: 'Mountain Time (US)' },
  { value: 'America/Los_Angeles', label: 'Pacific Time (US)' },
  { value: 'Europe/London', label: 'London' },
  { value: 'Europe/Paris', label: 'Paris' },
  { value: 'Asia/Tokyo', label: 'Tokyo' },
  { value: 'Asia/Shanghai', label: 'Shanghai' },
];

export const Settings: React.FC = () => {
  const [settings, setSettings] = useState<SettingsType>({
    email: '',
    company_name: '',
    timezone: 'UTC',
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const res = await getSettings();
        setSettings(res.data);
      } catch (error) {
        console.error('Error fetching settings:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchSettings();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateSettings({
        company_name: settings.company_name,
        timezone: settings.timezone,
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (error) {
      console.error('Error saving settings:', error);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-green-500 font-mono animate-pulse">Loading settings...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-mono font-bold text-white">Settings</h1>
        <p className="text-gray-400 mt-1">Manage your account preferences</p>
      </div>

      <Card>
        <h2 className="text-lg font-mono font-semibold text-green-500 mb-4">
          Account Settings
        </h2>

        <div className="space-y-4">
          <Input
            label="Account Email"
            value={settings.email}
            disabled
            className="opacity-50"
          />

          <Input
            label="Company Name"
            value={settings.company_name}
            onChange={(e) =>
              setSettings({ ...settings, company_name: e.target.value })
            }
            placeholder="Your company name"
          />

          <Select
            label="Timezone"
            value={settings.timezone}
            onChange={(e) =>
              setSettings({ ...settings, timezone: e.target.value })
            }
            options={timezones}
          />
        </div>

        <div className="flex items-center gap-4 mt-6 pt-4 border-t border-[#1a1a1a]">
          <Button onClick={handleSave} loading={saving}>
            {saved ? (
              <>
                <Check size={18} />
                Saved!
              </>
            ) : (
              'Save Changes'
            )}
          </Button>
          {saved && (
            <span className="text-green-500 text-sm animate-pulse">
              Settings updated successfully
            </span>
          )}
        </div>
      </Card>

      <Card>
        <h2 className="text-lg font-mono font-semibold text-green-500 mb-4">
          API Configuration
        </h2>
        <p className="text-gray-400 text-sm mb-4">
          OpenAI API key status for attack generation and evaluation.
        </p>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-yellow-500 animate-pulse" />
          <span className="text-gray-300 text-sm">
            Configure OPENAI_API_KEY environment variable for real attack testing
          </span>
        </div>
      </Card>
    </div>
  );
};
