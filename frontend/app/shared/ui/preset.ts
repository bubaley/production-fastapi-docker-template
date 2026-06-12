import { definePreset } from '@primeuix/themes'
import Aura from '@primeuix/themes/aura'

const BasePreset = definePreset(Aura, {
  semantic: {
    primary: {
      '50': '#edfff7',
      '100': '#d5ffed',
      '200': '#aeffdc',
      '300': '#70ffc4',
      '400': '#2bfda6',
      '500': '#00dc82',
      '600': '#00c072',
      '700': '#009659',
      '800': '#067549',
      '900': '#07603e',
      '950': '#003723',
    },
    formField: {
      borderRadius: 'var(--radius-sm)',
      paddingX: '0.6rem',
      paddingY: '0.4rem',
      sm: {
        paddingX: '0.4rem',
        paddingY: '0.18rem',
      },
    },
    colorScheme: {
      light: {
        primary: {
          color: '{primary.500}',
          contrastColor: '#000',
          hoverColor: '{primary.500}',
          activeColor: '{primary.400}',
        },
        content: {},
        formField: {
          disabledBackground: 'transparent',
        },
      },
      dark: {
        surface: {
          '50': '#f6f6f6',
          '100': '#e7e7e7',
          '200': '#d1d1d1',
          '300': '#b0b0b0',
          '400': '#888888',
          '500': '#6d6d6d',
          '600': '#5d5d5d',
          '700': '#2B2B2B',
          '800': '#1F1F1F',
          '900': '#1F1F1F',
          '950': '#111111',
          '1000': '#090909',
        },
        content: {
          hoverBackground: '{surface.900}',
          borderColor: '{surface.900}',
          color: 'var(--content-color)',
          hoverColor: '{text.hover.color}',
        },
        formField: {
          background: 'var(--bg-secondary)',
          borderColor: '{surface.800}',
          hoverBorderColor: '{surface.600}',
          color: 'var(--content-color)',
          disabledBackground: 'transparent',
          filledBackground: '{surface.900}',
          filledHoverBackground: '{surface.800}',
        },
        overlay: {
          popover: {
            background: 'var(--bg-secondary)',
            padding: '0rem',
          },
          modal: {
            background: 'var(--bg-secondary)',
            borderColor: '{surface.800}',
          },
          select: {
            background: 'var(--bg-secondary)',
            borderColor: '{surface.800}',
          },
        },
      },
    },
  },
  components: {
    datatable: {
      row: {
        background: 'transparent',
      },
      footerCell: {
        background: 'var(--bg-secondary)',
      },
      headerCell: {
        background: 'var(--bg-secondary)',
      },
      bodyCell: {
        // padding: "10px"
      },
      colorScheme: {
        dark: {
          root: {
            borderColor: '{surface.900}',
          },
        },
      },
    },
    paginator: {
      root: {
        background: 'transparent',
      },
    },
    tooltip: {
      root: {
        padding: '0.3rem 0.5rem',
      },
      colorScheme: {
        light: {
          root: {
            background: 'var(--bg-base)',
            color: 'var(--fg-secondary)',
          },
        },
        dark: {
          root: {
            background: 'var(--bg-base)',
            color: 'var(--fg-secondary)',
          },
        },
      },
    },
  },
})

export default {
  preset: BasePreset,
  options: {
    darkModeSelector: '[data-theme="dark"]',
  },
}
