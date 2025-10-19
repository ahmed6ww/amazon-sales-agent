import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  ...compat.extends("next/core-web-vitals", "next/typescript"),
  {
    ignores: [
      ".next/**/*",
      "next-env.d.ts",
      "out/**/*",
      "dist/**/*",
      "node_modules/**/*",
      "**/*.d.ts", // Ignore all type declaration files
    ],
  },
  {
    rules: {
      "@typescript-eslint/no-explicit-any": "off", // Allow 'any' type
      "@typescript-eslint/no-unused-vars": [
        "warn",
        {
          "argsIgnorePattern": "^_",
          "varsIgnorePattern": "^_",
          "caughtErrorsIgnorePattern": "^_",
          "destructuredArrayIgnorePattern": "^_",
          "ignoreRestSiblings": true
        }
      ],
    },
  },
];

export default eslintConfig;
