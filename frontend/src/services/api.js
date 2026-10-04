const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

async function handleResponse(response) {
  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`;
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errJson.error || errorDetail;
    } catch {
      // ignore parse error
    }
    throw new Error(errorDetail);
  }
  return response.json();
}

export const api = {
  async getHealth() {
    const res = await fetch(`${API_BASE}/api/health`);
    return handleResponse(res);
  },

  async getPresets() {
    const res = await fetch(`${API_BASE}/api/presets`);
    return handleResponse(res);
  },

  async getCanonicalSkills() {
    const res = await fetch(`${API_BASE}/api/skills/canonical`);
    return handleResponse(res);
  },

  async analyzeResumeFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/api/resume/analyze`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse(res);
  },

  async analyzeResumeText(resumeText, filename = 'resume.txt') {
    const res = await fetch(`${API_BASE}/api/resume/analyze-json`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resume_text: resumeText, filename }),
    });
    return handleResponse(res);
  },

  async analyzeJob(jobDescription, title = '', company = '') {
    const res = await fetch(`${API_BASE}/api/job/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_description: jobDescription, title, company }),
    });
    return handleResponse(res);
  },

  async match(candidate, job, resumeText = null, jobText = null) {
    const res = await fetch(`${API_BASE}/api/match`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        candidate,
        job,
        resume_text: resumeText,
        job_text: jobText,
      }),
    });
    return handleResponse(res);
  },

  async getSkillGaps(candidate, job) {
    const res = await fetch(`${API_BASE}/api/skill-gaps`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ candidate, job }),
    });
    return handleResponse(res);
  },

  async improveResume(candidate, resumeText = null) {
    const res = await fetch(`${API_BASE}/api/resume/improve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ candidate, resume_text: resumeText }),
    });
    return handleResponse(res);
  },

  async getRecommendations(candidate, jobs = null, topK = 5) {
    const res = await fetch(`${API_BASE}/api/recommendations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ candidate, jobs, top_k: topK }),
    });
    return handleResponse(res);
  },

  async getEvaluation() {
    const res = await fetch(`${API_BASE}/api/evaluation`);
    return handleResponse(res);
  },

  async runEvaluation() {
    const res = await fetch(`${API_BASE}/api/evaluation/run`, {
      method: 'POST',
    });
    return handleResponse(res);
  },
};

