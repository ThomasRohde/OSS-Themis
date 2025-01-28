import Cookies from 'js-cookie';
import React, { useEffect, useState } from 'react';
import { Toaster } from 'react-hot-toast';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { ApiClient } from './api/client';
import About from './components/About';
import Admin from './components/Admin';
import AuditLogs from './components/AuditLogs';
import BurgerMenu from './components/BurgerMenu';
import { CapabilityTree } from './components/CapabilityTree';
import SettingsComponent from './components/Settings';
import { Visualize } from './components/Visualize';
import { AppProvider, useApp } from './contexts/AppContext';
import { SettingsProvider, useSettings } from './contexts/SettingsContext';
import { TemplateSettings } from './types/api';

const LoginScreen: React.FC = () => {
  const { login } = useApp();
  const [nickname, setNickname] = useState(Cookies.get('nickname') || '');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(nickname);
      Cookies.set('nickname', nickname, { expires: 365 }); // Store for 1 year
    } catch (error) {
      console.error('Login error:', error);
      setError('Failed to login. Please try again.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full p-6 bg-white rounded-lg shadow-md">
        <h1 className="text-2xl font-bold text-center text-gray-900 mb-6">
          Business Capability Model
        </h1>
        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md">
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="nickname" className="block text-sm font-medium text-gray-700 mb-1">
              Nickname
            </label>
            <input
              id="nickname"
              type="text"
              value={nickname}
              onChange={(e) => setNickname(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
              aria-label="Enter your nickname"
              placeholder="Enter your nickname"
              required
              minLength={1}
              maxLength={50}
            />
          </div>
          <button
            type="submit"
            className="w-full py-2 px-4 bg-blue-500 text-white rounded-md hover:bg-blue-600"
          >
            Enter
          </button>
        </form>
      </div>
    </div>
  );
};

const MainApp: React.FC = () => {
  const { userSession, logout, activeUsers } = useApp();
  const { settings } = useSettings();

  // Helper function to get template display name
  const getTemplateDisplayName = (template: string | TemplateSettings) => {
    if (typeof template === 'string') {
      return template.replace('.j2', '').split('_').join(' ').charAt(0).toUpperCase() + template.replace('.j2', '').split('_').join(' ').slice(1);
    }
    return template.selected.replace('.j2', '').split('_').join(' ').charAt(0).toUpperCase() + template.selected.replace('.j2', '').split('_').join(' ').slice(1);
  };

  if (!userSession) {
    return <LoginScreen />;
  }

  // Create a reusable header component
  const Header = () => {
    const handleExport = async () => {
      try {
        const blob = await ApiClient.exportContext();
        const contentType = blob.type;
        const fileExtension = contentType === 'application/zip' ? '.zip' : '.md';
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `context-export${fileExtension}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } catch (error) {
        console.error('Export failed:', error);
      }
    };

    return (
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex justify-end items-center">
            <div className="flex items-center space-x-4">
              {settings && (
                <div className="px-4 py-2 bg-gray-50 rounded-lg border border-gray-200 shadow-sm">
                  <span className="text-sm font-medium text-gray-700">
                    Prompts: {getTemplateDisplayName(settings.first_level_template)} → {getTemplateDisplayName(settings.normal_template)} / Logged in as: {userSession.nickname} / Active users: {activeUsers.length}
                  </span>
                </div>
              )}
              <button
                onClick={handleExport}
                className="px-3 py-2 text-sm bg-green-500 text-white rounded-md hover:bg-green-600"
              >
                Export Context
              </button>
              <button
                onClick={() => ApiClient.clearLocks(userSession.session_id)}
                className="px-3 py-2 text-sm bg-yellow-500 text-white rounded-md hover:bg-yellow-600"
              >
                Clear Locks
              </button>
              <button
                onClick={logout}
                className="px-3 py-2 text-sm bg-red-500 text-white rounded-md hover:bg-red-600"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>
    );
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/visualize/:id"
          element={
            userSession ? (
              <Visualize sessionId={userSession.session_id} />
            ) : (
              <Navigate to="/" replace />
            )
          }
        />
        <Route
          path="/"
          element={
            <div className="min-h-screen bg-gray-50">
              <BurgerMenu />
              <Header />
              <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <CapabilityTree />
              </main>
            </div>
          }
        />
        {/* Replace all other route headers with the Header component */}
        <Route
          path="/about"
          element={
            <div className="min-h-screen bg-gray-50">
              <BurgerMenu />
              <Header />
              <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <About />
              </main>
            </div>
          }
        />
        <Route
          path="/settings"
          element={
            <div className="min-h-screen bg-gray-50">
              <BurgerMenu />
              <Header />
              <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <SettingsComponent />
              </main>
            </div>
          }
        />
        <Route
          path="/audit-logs"
          element={
            <div className="min-h-screen bg-gray-50">
              <BurgerMenu />
              <Header />
              <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <AuditLogs />
              </main>
            </div>
          }
        />
        <Route
          path="/admin"
          element={
            <div className="min-h-screen bg-gray-50">
              <BurgerMenu />
              <Header />
              <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <Admin />
              </main>
            </div>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

const App: React.FC = () => {
  useEffect(() => {
    const requestClipboardPermission = async () => {
      try {
        const result = await navigator.permissions.query({ name: 'clipboard-read' as PermissionName });
        if (result.state === 'prompt') {
          // This will trigger the permission prompt
          await navigator.clipboard.readText().catch(() => {
            // Ignore error if user denies permission
          });
        }
      } catch (error) {
        console.warn('Clipboard permission request failed:', error);
      }
    };

    requestClipboardPermission();
  }, []);

  return (
    <AppProvider>
      <SettingsProvider>
        <MainApp />
        <Toaster />
      </SettingsProvider>
    </AppProvider>
  );
};

export default App;
