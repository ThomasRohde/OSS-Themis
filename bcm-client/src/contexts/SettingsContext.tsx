import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { ApiClient } from '../api/client';
import { Settings } from '../types/api';

interface SettingsContextType {
  settings: Settings | null;
  loadSettings: () => Promise<void>;
  updateSettings: (newSettings: Settings) => Promise<void>;
}

const SettingsContext = createContext<SettingsContextType | null>(null);

export const useSettings = () => {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};

export const SettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [settings, setSettings] = useState<Settings | null>(null);

  const loadSettings = useCallback(async () => {
    try {
      const data = await ApiClient.getSettings();
      setSettings(data);
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  }, []);

  // Add this useEffect to load settings when provider mounts
  useEffect(() => {
    loadSettings();
  }, [loadSettings]);

  const updateSettings = useCallback(async (newSettings: Settings) => {
    try {
      await ApiClient.updateSettings(newSettings);
      setSettings(newSettings);
    } catch (error) {
      console.error('Failed to update settings:', error);
    }
  }, []);

  return (
    <SettingsContext.Provider value={{ settings, loadSettings, updateSettings }}>
      {children}
    </SettingsContext.Provider>
  );
};