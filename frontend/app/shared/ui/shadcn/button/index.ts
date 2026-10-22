import { cva, type VariantProps } from 'class-variance-authority'

export { default as Button } from './Button.vue'

export const buttonVariants = cva(
  'inline-flex shrink-0 items-center justify-center gap-2 font-medium whitespace-nowrap transition-[background-color,border-color,color,box-shadow] duration-150 outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:shrink-0',
  {
    variants: {
      variant: {
        default:
          'border border-primary bg-primary text-primary-foreground shadow-sm hover:bg-primary/90 active:bg-primary',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline: 'border border-input bg-transparent hover:bg-field-hover',
        secondary: 'border border-transparent bg-secondary text-secondary-foreground hover:bg-accent',
        ghost: 'hover:bg-field-hover hover:text-accent-foreground',
        link: 'text-primary underline-offset-4 hover:underline',
      },
      // Heights and text sizes come from the control tokens in theme.css.
      size: {
        default: 'h-control-md rounded-md px-4 text-control-md',
        xs: 'h-control-xs rounded-sm px-2.5 text-control-xs',
        sm: 'h-control-sm rounded-md px-3 text-control-sm',
        lg: 'h-control-lg rounded-md px-6 text-control-md',
        icon: 'size-control-md rounded-md',
        'icon-xs': 'size-control-xs rounded-sm',
        'icon-sm': 'size-control-sm rounded-md',
        'icon-lg': 'size-control-lg rounded-md',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  },
)

export type ButtonVariants = VariantProps<typeof buttonVariants>
