// Quiz intro/welcome screen
import { useNavigate } from 'react-router-dom';
import { Button, Card } from '../ui';

export default function QuizIntro() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <Card className="max-w-2xl w-full p-8 text-center">
        <div className="mb-8">
          <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center">
            <svg
              className="w-10 h-10 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"
              />
            </svg>
          </div>
          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-indigo-400 bg-clip-text text-transparent">
            Music Match
          </h1>
          <p className="text-xl text-slate-300 mb-2">
            Discover your perfect sound
          </p>
          <p className="text-slate-400">
            Answer a few questions about your music preferences and we'll find
            tracks that match your unique taste.
          </p>
        </div>

        <div className="space-y-4 mb-8">
          <div className="flex items-center gap-3 text-left p-3 rounded-lg bg-slate-700/30">
            <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center text-purple-400">
              1
            </div>
            <p className="text-slate-300">Answer 12 quick questions about your mood and preferences</p>
          </div>
          <div className="flex items-center gap-3 text-left p-3 rounded-lg bg-slate-700/30">
            <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center text-purple-400">
              2
            </div>
            <p className="text-slate-300">We analyze your responses to build your music profile</p>
          </div>
          <div className="flex items-center gap-3 text-left p-3 rounded-lg bg-slate-700/30">
            <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center text-purple-400">
              3
            </div>
            <p className="text-slate-300">Get personalized song recommendations that match your vibe</p>
          </div>
        </div>

        <Button size="lg" onClick={() => navigate('/quiz')}>
          Start the Quiz
        </Button>

        <p className="text-slate-500 text-sm mt-6">
          Takes about 2 minutes
        </p>
      </Card>
    </div>
  );
}
