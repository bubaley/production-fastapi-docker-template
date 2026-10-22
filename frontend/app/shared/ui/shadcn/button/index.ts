import { cva, type VariantProps } from 'class-variance-authority'

export { default as Button } from './Button.vue'

const defaultClasses = 'border border-foreground bg-foreground text-background shadow-sm hover:bg-foreground/90 active:bg-foreground'

export const buttonVariants = cva(
  'inline-flex shrink-0 items-center justify-center gap-2 whitespace-nowrap rounded-md font-medium transition-[background-color,border-color,color,box-shadow] duration-150 outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0',
  {
    variants: {
      variant: {
        default: defaultClasses,
        primary: 'border border-primary bg-primary text-primary-foreground hover:bg-primary/90 active:bg-primary',
        destructive: 'bg-destructive text-background hover:bg-destructive/90',
        outline: 'border border-input bg-transparent hover:bg-[color:var(--ds-field-hover)]',
        secondary: 'border border-transparent bg-secondary text-secondary-foreground hover:bg-accent',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'text-primary underline-offset-4 hover:underline'
      },
      size: {
        default: 'py-2',
        xs: 'rounded-md',
        sm: 'rounded-md',
        lg: 'rounded-md',
        icon: '',
        'icon-sm': 'rounded-md',
        'icon-xs': 'rounded-md',
        'icon-lg': 'rounded-md'
      }
    },
    defaultVariants: {
      variant: 'default',
      size: 'default'
    }
  }
)

export type ButtonVariants = VariantProps<typeof buttonVariants>
