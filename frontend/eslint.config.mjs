import nextConfig from "eslint-config-next";

const eslintConfig = [
  ...nextConfig,
  {
    ignores: ["next-env.d.ts", ".next/**", "out/**", "build/**", "node_modules/**"]
  }
];

export default eslintConfig;
