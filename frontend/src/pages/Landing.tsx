import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, Zap, FileText, TrendingUp, ChevronRight } from 'lucide-react';
import { Button } from '../components/Button';

const features = [
  {
    icon: Zap,
    title: 'Automated Attack Simulation',
    description: 'Run comprehensive red-team tests against your LLMs with AI-generated attack vectors.',
  },
  {
    icon: FileText,
    title: 'LLM Vulnerability Reports',
    description: 'Get detailed reports on jailbreaks, prompt injections, and data leakage risks.',
  },
  {
    icon: TrendingUp,
    title: 'Enterprise Risk Scoring',
    description: 'Track your security posture with severity-based risk assessments.',
  },
];

const steps = [
  {
    number: '01',
    title: 'Connect Your Model',
    description: 'Add your LLM endpoint with API credentials. Supports OpenAI-compatible APIs and custom HTTP.',
  },
  {
    number: '02',
    title: 'Run Security Tests',
    description: 'Our AI generates and executes attack prompts across multiple vulnerability categories.',
  },
  {
    number: '03',
    title: 'Review & Remediate',
    description: 'Analyze findings, get actionable recommendations, and improve your model security.',
  },
];

export const Landing: React.FC = () => {
  return (
    <div className="min-h-screen bg-black">
      <nav className="border-b border-[#1a1a1a] px-4 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Shield className="h-8 w-8 text-green-500" />
            <span className="font-mono font-bold text-green-500 text-lg text-glow">
              LLM Red Team Auditor
            </span>
          </div>
          <Link to="/login">
            <Button variant="outline" size="sm">
              Sign In
            </Button>
          </Link>
        </div>
      </nav>

      <section className="relative px-4 py-20 md:py-32 scanlines">
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-green-500/10 border border-green-500/30 mb-6">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-green-500 text-sm font-mono">Security Testing Platform</span>
          </div>

          <h1 className="text-4xl md:text-6xl font-mono font-bold text-white mb-6 text-glow">
            LLM Red Team
            <span className="block text-green-500">Auditor</span>
          </h1>

          <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
            Automated AI security testing for your language models. Discover vulnerabilities
            before attackers do.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/login">
              <Button size="lg" className="w-full sm:w-auto">
                Get Started
                <ChevronRight size={18} />
              </Button>
            </Link>
            <Link to="/app/dashboard">
              <Button variant="outline" size="lg" className="w-full sm:w-auto">
                View Demo
              </Button>
            </Link>
          </div>
        </div>

        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-green-500/5 rounded-full blur-3xl" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-green-500/5 rounded-full blur-3xl" />
        </div>
      </section>

      <section className="px-4 py-20 border-t border-[#1a1a1a]">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl md:text-3xl font-mono font-bold text-center text-white mb-12">
            Security Features
          </h2>

          <div className="grid md:grid-cols-3 gap-6">
            {features.map((feature) => {
              const Icon = feature.icon;
              return (
                <div
                  key={feature.title}
                  className="bg-[#0a0a0a] border border-[#1a1a1a] rounded-lg p-6 hover:border-green-500/30 transition-colors group"
                >
                  <div className="w-12 h-12 rounded-lg bg-green-500/10 flex items-center justify-center mb-4 group-hover:glow-green transition-shadow">
                    <Icon className="h-6 w-6 text-green-500" />
                  </div>
                  <h3 className="font-mono font-semibold text-white mb-2">{feature.title}</h3>
                  <p className="text-gray-400 text-sm">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="px-4 py-20 border-t border-[#1a1a1a]">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl md:text-3xl font-mono font-bold text-center text-white mb-12">
            How It Works
          </h2>

          <div className="space-y-8">
            {steps.map((step, index) => (
              <div
                key={step.number}
                className="flex gap-6 items-start"
              >
                <div className="flex-shrink-0 w-16 h-16 rounded-lg bg-green-500/10 border border-green-500/30 flex items-center justify-center">
                  <span className="font-mono font-bold text-green-500 text-xl">{step.number}</span>
                </div>
                <div className="flex-1 pt-2">
                  <h3 className="font-mono font-semibold text-white text-lg mb-2">{step.title}</h3>
                  <p className="text-gray-400">{step.description}</p>
                  {index < steps.length - 1 && (
                    <div className="w-px h-8 bg-[#1a1a1a] ml-8 mt-4" />
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t border-[#1a1a1a] px-4 py-8">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-green-500" />
            <span className="font-mono text-sm text-gray-400">LLM Red Team Auditor</span>
          </div>
          <div className="flex items-center gap-6">
            <a href="#" className="text-green-500 hover:text-green-400 text-sm">Privacy</a>
            <a href="#" className="text-green-500 hover:text-green-400 text-sm">Terms</a>
            <a href="#" className="text-green-500 hover:text-green-400 text-sm">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
};
