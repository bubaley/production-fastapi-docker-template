// @ts-check
import withNuxt from './.nuxt/eslint.config.mjs'
import pluginVue from 'eslint-plugin-vue'

export default withNuxt(
  ...pluginVue.configs['flat/recommended'],
  {
    rules: {
      'vue/singleline-html-element-content-newline': 'off',
      '@typescript-eslint/no-empty-object-type': 'off',
      'vue/no-mutating-props': 'off',
      'vue/valid-template-root': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
      'vue/require-default-prop': 'off',
      'vue/multi-word-component-names': 'off',
      'vue/no-v-html': 'off',
    },
  }
)
