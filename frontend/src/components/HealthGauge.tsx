import React from 'react';

interface HealthGaugeProps {
  score: number;
  grade: string;
  size?: number;
}

export const HealthGauge: React.FC<HealthGaugeProps> = ({ score, grade, size = 120 }) => {
  const strokeWidth = 10;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  let strokeColor = '#10b981'; // Emerald
  if (score < 60) strokeColor = '#f43f5e'; // Rose
  else if (score < 75) strokeColor = '#f59e0b'; // Amber
  else if (score < 90) strokeColor = '#0284c7'; // Sky

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#1e293b"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={strokeColor}
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center text-center">
        <span className="text-2xl font-bold tracking-tight text-white">{score}</span>
        <span className="text-xs font-bold uppercase tracking-wider px-1.5 py-0.2 rounded" style={{ color: strokeColor }}>
          Grade {grade}
        </span>
      </div>
    </div>
  );
};
