// Radar chart for user profile visualization
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import type { RadarDataPoint } from '../../types';

interface ProfileRadarProps {
  data: RadarDataPoint[];
  title?: string;
}

export default function ProfileRadar({ data, title = 'Your Music Profile' }: ProfileRadarProps) {
  return (
    <div className="w-full">
      {title && (
        <h3 className="text-lg font-semibold text-white mb-4 text-center">{title}</h3>
      )}
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data} cx="50%" cy="50%" outerRadius="80%">
            <PolarGrid stroke="#475569" />
            <PolarAngleAxis
              dataKey="feature"
              tick={{ fill: '#94a3b8', fontSize: 12 }}
            />
            <PolarRadiusAxis
              angle={30}
              domain={[0, 100]}
              tick={{ fill: '#64748b', fontSize: 10 }}
              axisLine={false}
            />
            <Radar
              name="Your Profile"
              dataKey="value"
              stroke="#a855f7"
              fill="#a855f7"
              fillOpacity={0.3}
              strokeWidth={2}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid #475569',
                borderRadius: '8px',
              }}
              labelStyle={{ color: '#f1f5f9' }}
              itemStyle={{ color: '#a855f7' }}
              formatter={(value: number) => [`${value.toFixed(1)}%`, 'Value']}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
