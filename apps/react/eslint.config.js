import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import tseslint from "typescript-eslint";
import rootConfig from "../../eslint.config.js";

export default tseslint.config(...rootConfig, {
  files: ["**/*.{ts,tsx}"],
  extends: [reactHooks.configs.flat.recommended, reactRefresh.configs.vite],
});
