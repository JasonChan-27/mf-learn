import tseslint from 'typescript-eslint'
import pluginVue from 'eslint-plugin-vue'
import rootConfig from '../../eslint.config.js'

export default tseslint.config(
  ...rootConfig,
  ...pluginVue.configs['flat/recommended'], // 专门给 Vue 3 增加的规则
  {
    files: ['*.vue', '**/*.vue'],
    languageOptions: {
      parserOptions: {
        parser: tseslint.parser,
      },
    },
    rules: {
      'vue/multi-word-component-names': 'off', // 常见的 Vue 规则调整
    },
  },
)
