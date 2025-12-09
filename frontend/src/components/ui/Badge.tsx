// UI Badge component
interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'info' | 'purple';
  className?: string;
}

export default function Badge({
  children,
  variant = 'default',
  className = '',
}: BadgeProps) {
  const baseClasses = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium';

  const variantClasses = {
    default: 'bg-slate-700 text-slate-300',
    success: 'bg-green-900/50 text-green-400 border border-green-500/30',
    warning: 'bg-yellow-900/50 text-yellow-400 border border-yellow-500/30',
    info: 'bg-blue-900/50 text-blue-400 border border-blue-500/30',
    purple: 'bg-purple-900/50 text-purple-400 border border-purple-500/30',
  };

  return (
    <span className={`${baseClasses} ${variantClasses[variant]} ${className}`}>
      {children}
    </span>
  );
}
