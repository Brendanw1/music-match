// Feature comparison between user profile and cluster centroid
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts';
import { Card } from '../ui';

interface ComparisonData {
  feature: string;
  user: number;
  cluster: number;
}

interface FeatureComparisonProps {
  userVector: Record<string, number>;
  clusterCentroid: Record<string, number>;
  title?: string;
}

const FEATURE_LABELS: Record<string, string> = {
  bpm_normalized: 'Tempo',
  energy: 'Energy',
  danceability: 'Danceability',
  acousticness: 'Acoustic',
  valence: 'Positivity',
  instrumentalness: 'Instrumental',
  loudness: 'Loudness',
};

export default function FeatureComparison({
  userVector,
  clusterCentroid,
  title = 'Profile vs Cluster Match',
}: FeatureComparisonProps) {
  // Build comparison data
  const data: ComparisonData[] = Object.keys(FEATURE_LABELS).map((key) => ({
    feature: FEATURE_LABELS[key],
    user: Math.round((userVector[key] || 0) * 100),
    cluster: Math.round((clusterCentroid[key] || 0) * 100),
  }));

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold text-white mb-4">{title}</h3>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data} cx="50%" cy="50%" outerRadius="80%">
            <PolarGrid stroke="#475569" />
            <PolarAngleAxis
              dataKey="feature"
              tick={{ fill: '#94a3b8', fontSize: 11 }}
            />
            <PolarRadiusAxis
              angle={30}
              domain={[0, 100]}
              tick={{ fill: '#64748b', fontSize: 10 }}
              axisLine={false}
            />
            <Radar
              name="Your Profile"
              dataKey="user"
              stroke="#a855f7"
              fill="#a855f7"
              fillOpacity={0.3}
              strokeWidth={2}
            />
            <Radar
              name="Cluster Center"
              dataKey="cluster"
              stroke="#22c55e"
              fill="#22c55e"
              fillOpacity={0.2}
              strokeWidth={2}
            />
            <Legend
              wrapperStyle={{
                paddingTop: '20px',
              }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid #475569',
                borderRadius: '8px',
              }}
              labelStyle={{ color: '#f1f5f9' }}
              formatter={(value: number, name: string) => [
                `${value}%`,
                name === 'user' ? 'Your Profile' : 'Cluster Center',
              ]}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
