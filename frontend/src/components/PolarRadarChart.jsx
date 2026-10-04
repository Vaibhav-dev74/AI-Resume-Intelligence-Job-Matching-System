import React from 'react';

export default function PolarRadarChart({
  breakdown = {},
  size = 320,
}) {
  const cx = size / 2;
  const cy = size / 2;
  const radius = size * 0.38;

  const axes = [
    { key: 'required_skills', label: 'Required Skills', fallbackScore: 0 },
    { key: 'preferred_skills', label: 'Preferred Skills', fallbackScore: 0 },
    { key: 'semantic_similarity', label: 'Semantic Text', fallbackScore: 0 },
    { key: 'experience_duration', label: 'Experience', fallbackScore: 0 },
    { key: 'project_relevance', label: 'Projects', fallbackScore: 0 },
    { key: 'education_level', label: 'Education', fallbackScore: 0 },
  ];

  const totalAxes = axes.length;
  const levels = [0.25, 0.5, 0.75, 1.0];

  const getCoordinates = (index, valuePercent) => {
    const angle = (Math.PI * 2 / totalAxes) * index - Math.PI / 2;
    const r = radius * (valuePercent / 100);
    return {
      x: cx + r * Math.cos(angle),
      y: cy + r * Math.sin(angle),
    };
  };

  const polygonPoints = axes.map((axis, i) => {
    const score = breakdown[axis.key]?.score ?? axis.fallbackScore;
    const { x, y } = getCoordinates(i, score);
    return `${x},${y}`;
  }).join(' ');

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size} className="overflow-visible">
        {/* Background Concentric Webs */}
        {levels.map((lvl) => {
          const points = axes.map((_, i) => {
            const { x, y } = getCoordinates(i, lvl * 100);
            return `${x},${y}`;
          }).join(' ');
          return (
            <polygon
              key={lvl}
              points={points}
              fill="none"
              stroke="rgba(255, 255, 255, 0.08)"
              strokeWidth="1"
            />
          );
        })}

        {/* Radial Axis Lines */}
        {axes.map((_, i) => {
          const { x, y } = getCoordinates(i, 100);
          return (
            <line
              key={i}
              x1={cx}
              y1={cy}
              x2={x}
              y2={y}
              stroke="rgba(255, 255, 255, 0.12)"
              strokeWidth="1"
              strokeDasharray="2,2"
            />
          );
        })}

        {/* Data Polygon Fill */}
        <polygon
          points={polygonPoints}
          fill="rgba(99, 102, 241, 0.25)"
          stroke="#818CF8"
          strokeWidth="2.5"
          className="transition-all duration-700 ease-out"
        />

        {/* Data Points */}
        {axes.map((axis, i) => {
          const score = breakdown[axis.key]?.score ?? axis.fallbackScore;
          const { x, y } = getCoordinates(i, score);
          return (
            <circle
              key={i}
              cx={x}
              cy={y}
              r="4.5"
              fill="#6366F1"
              stroke="#FFFFFF"
              strokeWidth="2"
              className="transition-all duration-700 ease-out"
            />
          );
        })}

        {/* Axis Labels */}
        {axes.map((axis, i) => {
          const { x, y } = getCoordinates(i, 116);
          const score = breakdown[axis.key]?.score ?? axis.fallbackScore;
          return (
            <g key={i}>
              <text
                x={x}
                y={y}
                textAnchor="middle"
                dominantBaseline="central"
                className="fill-slate-300 text-[10px] font-medium tracking-wide"
              >
                {axis.label}
              </text>
              <text
                x={x}
                y={y + 11}
                textAnchor="middle"
                dominantBaseline="central"
                className="fill-indigo-400 text-[9px] font-mono font-bold"
              >
                {Math.round(score)}%
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

