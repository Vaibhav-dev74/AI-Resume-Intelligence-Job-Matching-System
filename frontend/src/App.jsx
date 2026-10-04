import React from 'react';
import { AppProvider, useApp } from './context/AppContext';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Overview from './pages/Overview';
import Workspace from './pages/Workspace';
import MatchAnalysis from './pages/MatchAnalysis';
import SkillGaps from './pages/SkillGaps';
import ResumeImprovement from './pages/ResumeImprovement';
import JobRecommendations from './pages/JobRecommendations';
import Architecture from './pages/Architecture';
import SkillOntology from './pages/SkillOntology';
import Evaluation from './pages/Evaluation';

function MainContent() {
  const { activeTab } = useApp();

  return (
    <main className="flex-1 p-6 lg:p-10 overflow-y-auto max-h-[calc(100vh-61px)]">
      {activeTab === 'overview' && <Overview />}
      {activeTab === 'workspace' && <Workspace />}
      {activeTab === 'match' && <MatchAnalysis />}
      {activeTab === 'gaps' && <SkillGaps />}
      {activeTab === 'improve' && <ResumeImprovement />}
      {activeTab === 'recommendations' && <JobRecommendations />}
      {activeTab === 'architecture' && <Architecture />}
      {activeTab === 'ontology' && <SkillOntology />}
      {activeTab === 'evaluation' && <Evaluation />}
    </main>
  );
}

export default function App() {
  return (
    <AppProvider>
      <div className="min-h-screen bg-[#070B13] text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white">
        <Navbar />
        <div className="flex flex-1 overflow-hidden">
          <Sidebar />
          <MainContent />
        </div>
      </div>
    </AppProvider>
  );
}

