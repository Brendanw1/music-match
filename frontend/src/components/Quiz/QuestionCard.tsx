// Single quiz question display
import type { QuizQuestion } from '../../types';
import { Card } from '../ui';

interface QuestionCardProps {
  question: QuizQuestion;
  selectedOption: string | null;
  onSelectOption: (optionId: string) => void;
}

export default function QuestionCard({
  question,
  selectedOption,
  onSelectOption,
}: QuestionCardProps) {
  return (
    <div className="w-full max-w-2xl mx-auto">
      <h2 className="text-2xl font-semibold text-white mb-8 text-center">
        {question.question}
      </h2>

      <div className="grid gap-3">
        {question.options.map((option) => (
          <Card
            key={option.id}
            variant={selectedOption === option.id ? 'highlighted' : 'interactive'}
            className={`p-4 ${
              selectedOption === option.id
                ? 'ring-2 ring-purple-500'
                : ''
            }`}
            onClick={() => onSelectOption(option.id)}
          >
            <div className="flex items-center gap-4">
              <div
                className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all ${
                  selectedOption === option.id
                    ? 'border-purple-500 bg-purple-500'
                    : 'border-slate-500'
                }`}
              >
                {selectedOption === option.id && (
                  <svg
                    className="w-4 h-4 text-white"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                )}
              </div>
              <span className="text-slate-200 text-lg">{option.text}</span>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
