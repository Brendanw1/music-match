// Quiz state management and navigation
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import type { QuizQuestion, QuizAnswer, QuizResult } from '../../types';
import { quizApi } from '../../api/client';
import { Button, Loading, ProgressBar } from '../ui';
import QuestionCard from './QuestionCard';

export default function QuizContainer() {
  const navigate = useNavigate();
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Map<string, string>>(new Map());
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadQuestions();
  }, []);

  const loadQuestions = async () => {
    try {
      setLoading(true);
      const data = await quizApi.getQuestions();
      setQuestions(data);
      setError(null);
    } catch (err) {
      setError('Failed to load quiz questions. Please try again.');
      console.error('Failed to load questions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectOption = (optionId: string) => {
    const currentQuestion = questions[currentIndex];
    const newAnswers = new Map(answers);
    newAnswers.set(currentQuestion.id, optionId);
    setAnswers(newAnswers);
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const handleSubmit = async () => {
    try {
      setSubmitting(true);

      const quizAnswers: QuizAnswer[] = Array.from(answers.entries()).map(
        ([questionId, optionId]) => ({
          question_id: questionId,
          option_id: optionId,
        })
      );

      const result = await quizApi.submitQuiz(quizAnswers);

      // Store result in session storage for the results page
      sessionStorage.setItem('quizResult', JSON.stringify(result));

      navigate('/results');
    } catch (err) {
      setError('Failed to submit quiz. Please try again.');
      console.error('Failed to submit quiz:', err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loading size="lg" text="Loading quiz..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="text-center">
          <p className="text-red-400 mb-4">{error}</p>
          <Button onClick={loadQuestions}>Try Again</Button>
        </div>
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <p className="text-slate-400">No questions available.</p>
      </div>
    );
  }

  const currentQuestion = questions[currentIndex];
  const currentAnswer = answers.get(currentQuestion.id) || null;
  const isLastQuestion = currentIndex === questions.length - 1;
  const allAnswered = answers.size === questions.length;

  return (
    <div className="min-h-screen flex flex-col p-4">
      {/* Header */}
      <header className="max-w-2xl mx-auto w-full pt-8 pb-4">
        <ProgressBar current={currentIndex + 1} total={questions.length} />
      </header>

      {/* Main content */}
      <main className="flex-1 flex items-center justify-center py-8">
        <QuestionCard
          question={currentQuestion}
          selectedOption={currentAnswer}
          onSelectOption={handleSelectOption}
        />
      </main>

      {/* Navigation */}
      <footer className="max-w-2xl mx-auto w-full pb-8">
        <div className="flex justify-between items-center">
          <Button
            variant="ghost"
            onClick={handlePrevious}
            disabled={currentIndex === 0}
          >
            Previous
          </Button>

          <div className="flex gap-2">
            {!isLastQuestion ? (
              <Button
                onClick={handleNext}
                disabled={!currentAnswer}
              >
                Next
              </Button>
            ) : (
              <Button
                onClick={handleSubmit}
                disabled={!allAnswered || submitting}
              >
                {submitting ? 'Analyzing...' : 'See My Results'}
              </Button>
            )}
          </div>
        </div>
      </footer>
    </div>
  );
}
