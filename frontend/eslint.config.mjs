// @ts-check
// ESLint runs only on Vue SFCs to cover <template> rules that Oxlint does not implement.
// Script rules live in the Vite+ `lint` block (vite.config.ts); eslint-plugin-oxlint turns off the overlap.
import tsParser from '@typescript-eslint/parser'
import oxlint from 'eslint-plugin-oxlint'
import pluginVue from 'eslint-plugin-vue'
import viteConfig from './vite.config.ts'

// Oxfmt owns layout, so stylistic template rules would only fight the formatter.
const layoutRulesOff = Object.fromEntries(
  Object.entries(pluginVue.rules ?? {})
    .filter(([, rule]) => rule.meta?.type === 'layout')
    .map(([name]) => [`vue/${name}`, 'off']),
)

export default [
  { ignores: ['**/node_modules/**', '.nuxt/**', '.output/**', '.data/**', 'dist/**', 'coverage/**', '.cache/**'] },
  ...pluginVue.configs['flat/recommended'],
  {
    files: ['**/*.vue'],
    languageOptions: { parserOptions: { parser: tsParser } },
    rules: {
      ...layoutRulesOff,
      // Redirect pages and renderless components deliberately have empty templates.
      'vue/valid-template-root': 'off',
      // Optional props are typed as `prop?: T`; `undefined` is the intended default.
      'vue/require-default-prop': 'off',
      // shadcn primitives use single-word names (Button, Input, Textarea).
      'vue/multi-word-component-names': 'off',
    },
  },
  ...oxlint.buildFromOxlintConfig(viteConfig.lint ?? {}),
]
