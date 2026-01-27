import React, { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  FolderKanban,
  FileText,
  Settings,
  LogOut,
  Menu,
  X,
  Shield,
  Sun,
  Moon,
  Lock,
  Activity,
} from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

const navItems = [
  { path: '/app/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/app/projects', label: 'Projects', icon: FolderKanban },
  { path: '/app/api-testing', label: 'API Testing', icon: Lock },
  { path: '/app/monitoring', label: 'Monitoring', icon: Activity },
  { path: '/app/reports', label: 'Reports', icon: FileText },
  { path: '/app/settings', label: 'Settings', icon: Settings },
];

export const AppLayout: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { theme, toggleTheme } = useTheme();

  const handleLogout = () => {
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-light-bg dark:bg-black flex transition-colors duration-300">
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-[#0a0a0a] border-r border-gray-200 dark:border-[#1a1a1a] transform transition-all duration-300 lg:translate-x-0 lg:static ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex flex-col h-full">
          <div className="p-4 border-b border-gray-200 dark:border-[#1a1a1a]">
            <Link to="/app/dashboard" className="flex items-center gap-3">
              <img
                src={theme === 'dark' ? '/white_logo.png' : '/black_logo.png'}
                alt="Valkyrie Logo"
                className="h-10 w-10 object-contain"
                onError={(e) => {
                  // Fallback to shield icon if logo not found
                  e.currentTarget.style.display = 'none';
                  e.currentTarget.nextElementSibling?.classList.remove('hidden');
                }}
              />
              <Shield className="h-8 w-8 text-green-500 hidden" />
              <div>
                <h1 className="text-green-500 font-mono font-bold text-lg leading-tight dark:text-glow">
                  Valkyrie
                </h1>
              </div>
            </Link>
          </div>

          <nav className="flex-1 p-4 space-y-1">
            {navItems.map((item) => {
              const isActive = location.pathname.startsWith(item.path);
              const Icon = item.icon;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setSidebarOpen(false)}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-green-500/10 text-green-600 dark:text-green-500 border border-green-500/30'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-[#1a1a1a] hover:text-gray-900 dark:hover:text-white'
                  }`}
                >
                  <Icon size={18} />
                  <span className="font-medium">{item.label}</span>
                </Link>
              );
            })}
          </nav>

          <div className="p-4 border-t border-gray-200 dark:border-[#1a1a1a]">
            <button
              onClick={handleLogout}
              className="flex items-center gap-3 px-3 py-2 w-full rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-[#1a1a1a] hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              <LogOut size={18} />
              <span className="font-medium">Logout</span>
            </button>
          </div>
        </div>
      </aside>

      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <div className="flex-1 flex flex-col min-h-screen">
        <header className="sticky top-0 z-30 bg-white/95 dark:bg-[#0a0a0a]/95 backdrop-blur border-b border-gray-200 dark:border-[#1a1a1a] transition-colors duration-300">
          <div className="flex items-center justify-between px-4 py-3">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-2 hover:bg-gray-100 dark:hover:bg-[#1a1a1a] rounded-lg text-gray-600 dark:text-gray-400 transition-colors"
              >
                {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
              </button>
              <div className="font-mono text-sm text-gray-600 dark:text-gray-400">
                {location.pathname.split('/').filter(Boolean).join(' / ')}
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={toggleTheme}
                className="p-2 hover:bg-gray-100 dark:hover:bg-[#1a1a1a] rounded-lg text-gray-600 dark:text-gray-400 hover:text-green-600 dark:hover:text-green-500 transition-colors"
                title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
              </button>
              <div className="hidden sm:flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-green-500/20 border border-green-500/30 flex items-center justify-center">
                  <span className="text-green-500 font-mono text-sm font-bold">S</span>
                </div>
                <span className="text-gray-600 dark:text-gray-400 text-sm">security@company.com</span>
              </div>
            </div>
          </div>
        </header>

        <main className="flex-1 p-4 md:p-6 overflow-auto bg-light-bg dark:bg-black transition-colors duration-300">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
