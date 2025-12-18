import js from '@eslint/js'
import tseslint from 'typescript-eslint'
import { globalIgnores } from 'eslint/config'
import eslintConfigPrettier from 'eslint-config-prettier'

export default tseslint.config(
  globalIgnores(['dist']),
  js.configs.recommended,
  ...tseslint.configs.flat.recommended,
  {
    rules: {},
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
  },
  eslintConfigPrettier, // 必须放在最后，用于关闭所有与 Prettier 冲突的 ESLint 规则
)
