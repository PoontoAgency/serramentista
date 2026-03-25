import { forwardRef, type InputHTMLAttributes } from 'react'
import { cn } from '../../lib/utils'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  hint?: string
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, hint, id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, '-')

    return (
      <div className="space-y-1.5">
        {label && (
          <label htmlFor={inputId} className="block text-sm font-medium text-neutral-900">
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={cn(
            'w-full px-3.5 py-2.5 rounded-lg text-sm text-neutral-900 bg-white',
            'border transition-all duration-200',
            'placeholder:text-neutral-600/50',
            'focus:outline-none focus:ring-2 focus:ring-offset-0',
            'disabled:opacity-50 disabled:bg-neutral-50',
            error
              ? 'border-danger focus:ring-danger/30 focus:border-danger'
              : 'border-neutral-200 focus:ring-primary/30 focus:border-primary',
            className
          )}
          {...props}
        />
        {error && (
          <p className="text-xs text-danger font-medium">{error}</p>
        )}
        {hint && !error && (
          <p className="text-xs text-neutral-600">{hint}</p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'
export default Input
