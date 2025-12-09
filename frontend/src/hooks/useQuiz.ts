// Quiz state management hook
import { useState, useCallback } from 'react';
import type { QuizQuestion, QuizAnswer, QuizResult } from '../types';
import { quizApi } from '../api/client';

interface UseQuizState {
  questions: QuizQuestion[];
  currentIndex: number;
  answers: Map<string, string>;
  result: QuizResult | null;
  loading: boolean;
  submitting: boolean;
  error: string | null;
}

export function useQuiz() {
  const [state, setState] = useState<UseQuizState>({
    questions: [],
    currentIndex: 0,
    answers: new Map(),
    result: null,
    loading: false,
    submitting: false,
    error: null,
  });

  const loadQuestions = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const questions = await quizApi.getQuestions();
      setState((prev) => ({ ...prev, questions, loading: false }));
    } catch (err) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: 'Failed to load quiz questions',
      }));
    }
  }, []);

  const setAnswer = useCallback((questionId: string, optionId: string) => {
    setState((prev) => {
      const newAnswers = new Map(prev.answers);
      newAnswers.set(questionId, optionId);
      return { ...prev, answers: newAnswers };
    });
  }, []);

  const nextQuestion = useCallback(() => {
    setState((prev) => ({
      ...prev,
      currentIndex: Math.min(prev.currentIndex + 1, prev.questions.length - 1),
    }));
  }, []);

  const previousQuestion = useCallback(() => {
    setState((prev) => ({
      ...prev,
      currentIndex: Math.max(prev.currentIndex - 1, 0),
    }));
  }, []);

  const submitQuiz = useCallback(async () => {
    setState((prev) => ({ ...prev, submitting: true, error: null }));
    try {
      const quizAnswers: QuizAnswer[] = Array.from(state.answers.entries()).map(
        ([questionId, optionId]) => ({
          question_id: questionId,
          option_id: optionId,
        })
      );
      const result = await quizApi.submitQuiz(quizAnswers);
      setState((prev) => ({ ...prev, result, submitting: false }));
      return result;
    } catch (err) {
      setState((prev) => ({
        ...prev,
        submitting: false,
        error: 'Failed to submit quiz',
      }));
      throw err;
    }
  }, [state.answers]);

  const reset = useCallback(() => {
    setState({
      questions: [],
      currentIndex: 0,
      answers: new Map(),
      result: null,
      loading: false,
      submitting: false,
      error: null,
    });
  }, []);

  return {
    ...state,
    currentQuestion: state.questions[state.currentIndex] || null,
    currentAnswer: state.answers.get(
      state.questions[state.currentIndex]?.id || ''
    ) || null,
    isFirstQuestion: state.currentIndex === 0,
    isLastQuestion: state.currentIndex === state.questions.length - 1,
    allAnswered: state.answers.size === state.questions.length,
    progress: state.questions.length
      ? ((state.currentIndex + 1) / state.questions.length) * 100
      : 0,
    loadQuestions,
    setAnswer,
    nextQuestion,
    previousQuestion,
    submitQuiz,
    reset,
  };
}
