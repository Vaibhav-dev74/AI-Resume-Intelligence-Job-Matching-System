import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

const AppContext = createContext();

export function AppProvider({ children }) {
  const [activeTab, setActiveTab] = useState('overview');
  const [presets, setPresets] = useState({ resumes: {}, jobs: {} });
  const [canonicalSkills, setCanonicalSkills] = useState([]);
  const [systemHealth, setSystemHealth] = useState(null);

  // Active analysis state
  const [candidateProfile, setCandidateProfile] = useState(null);
  const [candidateRawText, setCandidateRawText] = useState('');
  const [candidateFilename, setCandidateFilename] = useState('');

  const [jobData, setJobData] = useState(null);
  const [jobRawText, setJobRawText] = useState('');

  const [matchResult, setMatchResult] = useState(null);
  const [improvementResult, setImprovementResult] = useState(null);
  const [recommendations, setRecommendations] = useState(null);

  // Status & error handling
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [error, setError] = useState(null);

  // Initial load
  useEffect(() => {
    async function initPlatform() {
      try {
        const [health, presetData, canonSkills] = await Promise.allSettled([
          api.getHealth(),
          api.getPresets(),
          api.getCanonicalSkills(),
        ]);

        if (health.status === 'fulfilled') setSystemHealth(health.value);
        if (presetData.status === 'fulfilled') setPresets(presetData.value);
        if (canonSkills.status === 'fulfilled') setCanonicalSkills(canonSkills.value);
      } catch (err) {
        console.error('Platform initialization failed:', err);
      }
    }
    initPlatform();
  }, []);

  const selectPresetResume = (name) => {
    const item = presets.resumes[name];
    if (!item) return;
    setCandidateProfile(item.profile);
    setCandidateRawText(item.raw_text);
    setCandidateFilename(`${name}.txt`);
    setMatchResult(null);
    setImprovementResult(null);
    setRecommendations(null);
  };

  const selectPresetJob = (name) => {
    const item = presets.jobs[name];
    if (!item) return;
    setJobData(item.job_data);
    setJobRawText(item.raw_text);
    setMatchResult(null);
  };

  const executeMatch = async (customCand = null, customJob = null) => {
    const cand = customCand || candidateProfile;
    const job = customJob || jobData;

    if (!cand || !job) {
      setError('Please provide both candidate profile and target job description.');
      return null;
    }

    setLoading(true);
    setLoadingMessage('Executing 8-layer matching engine with sentence embeddings...');
    setError(null);

    try {
      const result = await api.match(cand, job, candidateRawText, jobRawText);
      setMatchResult(result);
      setActiveTab('match');
      return result;
    } catch (err) {
      setError(err.message || 'Matching failed');
      return null;
    } finally {
      setLoading(false);
      setLoadingMessage('');
    }
  };

  return (
    <AppContext.Provider
      value={{
        activeTab,
        setActiveTab,
        presets,
        canonicalSkills,
        systemHealth,
        candidateProfile,
        setCandidateProfile,
        candidateRawText,
        setCandidateRawText,
        candidateFilename,
        setCandidateFilename,
        jobData,
        setJobData,
        jobRawText,
        setJobRawText,
        matchResult,
        setMatchResult,
        improvementResult,
        setImprovementResult,
        recommendations,
        setRecommendations,
        loading,
        setLoading,
        loadingMessage,
        setLoadingMessage,
        error,
        setError,
        selectPresetResume,
        selectPresetJob,
        executeMatch,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}

