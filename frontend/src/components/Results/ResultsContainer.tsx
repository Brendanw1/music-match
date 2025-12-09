// Results page orchestrator
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { QuizResult } from '../../types';
import { Button, Card, Loading } from '../ui';
import ProfileRadar from './ProfileRadar';
import ClusterMatch from './ClusterMatch';
import AdjacentClusters from './AdjacentClusters';
import { RecommendationGrid } from '../Recommendations';

export default function ResultsContainer() {
  const navigate = useNavigate();
  const [result, setResult] = useState<QuizResult | null>(null);

  useEffect(() => {
    // Load result from session storage
    const stored = sessionStorage.getItem('quizResult');
    if (stored) {
      try {
        setResult(JSON.parse(stored));
      } catch {
        navigate('/');
      }
    } else {
      navigate('/');
    }
  }, [navigate]);

  if (!result) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loading size="lg" text="Loading results..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-2">Your Results</h1>
          <p className="text-slate-400">
            Based on your quiz answers, here's your personalized music profile
          </p>
        </header>

        {/* Main content grid */}
        <div className="grid gap-8 lg:grid-cols-2 mb-12">
          {/* Profile radar */}
          <Card className="p-6">
            <ProfileRadar data={result.user_profile.radar_chart_data} />
          </Card>

          {/* Matched cluster */}
          <ClusterMatch cluster={result.matched_cluster} />
        </div>

        {/* Recommendations */}
        {result.songs && result.songs.length > 0 && (
          <section className="mb-12">
            <h2 className="text-2xl font-bold text-white mb-6">
              Recommended for You
            </h2>
            <RecommendationGrid
              songs={result.songs}
              userVector={result.user_profile.feature_vector}
            />
          </section>
        )}

        {/* Adjacent clusters */}
        {result.adjacent_clusters && result.adjacent_clusters.length > 0 && (
          <section className="mb-12">
            <AdjacentClusters clusters={result.adjacent_clusters} />
          </section>
        )}

        {/* Actions */}
        <footer className="flex justify-center gap-4">
          <Button variant="outline" onClick={() => navigate('/explore')}>
            Explore All Clusters
          </Button>
          <Button onClick={() => navigate('/')}>
            Take Quiz Again
          </Button>
        </footer>
      </div>
    </div>
  );
}
