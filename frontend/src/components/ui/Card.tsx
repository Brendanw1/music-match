// UI Card component
interface CardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'interactive' | 'highlighted';
  onClick?: () => void;
}

export default function Card({
  children,
  className = '',
  variant = 'default',
  onClick,
}: CardProps) {
  const baseClasses = 'rounded-xl backdrop-blur-sm';

  const variantClasses = {
    default: 'bg-slate-800/50 border border-slate-700/50',
    interactive: 'bg-slate-800/50 border border-slate-700/50 hover:border-purple-500/50 hover:bg-slate-800/70 cursor-pointer transition-all duration-200',
    highlighted: 'bg-gradient-to-br from-purple-900/50 to-indigo-900/50 border border-purple-500/30',
  };

  return (
    <div
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      {children}
    </div>
  );
}
