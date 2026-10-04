import React from 'react';

export default function ScoreGauge({ score = 0, size = 180, strokeWidth = 14, title = "Match Score" }) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const validScore = Math.max(0, Math.min(100, Number(score) || 0));
  const strokeDashoffset = circumference - (validScore / 100) * circumference;

  let color = '#10B981'; // emerald
  let statusText = 'Strong Match';
  let badgeBg = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';

  if (validScore < 65) {
    color = '#F59E0B'; // amber
    statusText = 'Developing Fit';
    badgeBg = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
  } else if (validScore < 80) {
    color = '#6366F1'; // indigo
    statusText = 'Moderate Fit';
    badgeBg = 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30';
  }

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg className="w-full h-full transform -rotate-90" viewBox={`0 0 ${size} ${size}`}>
          {/* Background Track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            className="text-slate-800"
            fill="transparent"
          />
          {/* Active Fill */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-1000 ease-out"
          />
        </svg>

        {/* Center Text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className="text-4xl font-extrabold text-white tracking-tight">
            {validScore.toFixed(1)}
            <span className="text-xl font-normal text-slate-400">%</span>
          </span>
          <span className="text-xs uppercase tracking-wider text-slate-400 font-medium mt-0.5">
            {title}
          </span>
        </div>
      </div>

      <div className={`mt-3 px-3 py-1 rounded-full text-xs font-semibold border ${badgeBg}`}>
        {statusText}
      </div>
    </div>
  );
}

