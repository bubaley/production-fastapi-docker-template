import { type ClassValue, clsx } from 'clsx'
import { extendTailwindMerge } from 'tailwind-merge'

// Teach tailwind-merge the custom scales from theme.css, otherwise `text-control-sm` is read as a color
// and would drop `text-foreground` (and vice versa).
const twMerge = extendTailwindMerge({
  extend: {
    theme: {
      text: ['control-xs', 'control-sm', 'control-md'],
      spacing: ['control-xs', 'control-sm', 'control-md', 'control-lg'],
      shadow: ['overlay'],
    },
  },
})

export const cn = (...inputs: ClassValue[]) => twMerge(clsx(inputs))
