import { defineConfig } from "tsdown";

export default defineConfig({
  entry: [
    "src/accordion/index.ts",
    "src/animated-counter/index.ts",
    "src/avatar/index.ts",
    "src/button/index.ts",
    "src/calendar/index.ts",
    "src/card/index.ts",
    "src/charts/*/index.ts",
    "src/collapsible/index.ts",
    "src/combobox/index.ts",
    "src/command/index.ts",
    "src/context-menu/index.ts",
    "src/dialog/index.ts",
    "src/empty-state/index.ts",
    "src/emoji-icon-picker/index.ts",
    "src/emoji-reaction/index.ts",
    "src/emoji-reaction-picker/index.ts",
    "src/icons/index.ts",
    "src/input/index.ts",
    "src/menu/index.ts",
    "src/pill/index.ts",
    "src/popover/index.ts",
    "src/portal/index.ts",
    "src/scrollarea/index.ts",
    "src/skeleton/index.ts",
    "src/switch/index.ts",
    "src/table/index.ts",
    "src/tabs/index.ts",
    "src/toast/index.ts",
    "src/toolbar/index.ts",
    "src/tooltip/index.ts",
    "src/utils/index.ts",
  ],
  outDir: "dist",
  format: ["esm", "cjs"],
  exports: {
    customExports: (out) => {
      const fixedExports: typeof out = {};
      for (const [key, value] of Object.entries(out)) {
        // Fix key: replace backslashes with forward slashes
        let newKey = key.replace(/\\/g, "/");
        // Remove /index suffix if present to allow 'import ... from "@plane/propel/accordion"'
        if (newKey.endsWith("/index")) {
          newKey = newKey.replace(/\/index$/, "");
        }

        // Fix value: replace backslashes in paths
        const fixPath = (path: string) => path.replace(/\\/g, "/");
        const fixedValue =
          typeof value === "string"
            ? fixPath(value)
            : {
              import: fixPath((value as any).import),
              require: fixPath((value as any).require),
            };

        fixedExports[newKey] = fixedValue;
      }

      return {
        ...fixedExports,
        "./styles/fonts": "./dist/styles/fonts/index.css",
        "./styles/react-day-picker": "./dist/styles/react-day-picker.css",
      };
    },
  },
  copy: ["src/styles"],
  dts: true,
  clean: true,
  sourcemap: false,
});
