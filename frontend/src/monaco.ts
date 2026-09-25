// Bundle Monaco locally (no CDN) with only the Python language.
import { loader } from "@monaco-editor/react";
import * as monaco from "monaco-editor/esm/vs/editor/editor.api";
import "monaco-editor/esm/vs/basic-languages/python/python.contribution";
import EditorWorker from "monaco-editor/esm/vs/editor/editor.worker?worker";

self.MonacoEnvironment = { getWorker: () => new EditorWorker() };
loader.config({ monaco });

monaco.editor.defineTheme("kodetrain-light", {
  base: "vs", inherit: true, rules: [],
  colors: { "editor.background": "#FBFCFE", "editorLineNumber.foreground": "#8690A8", "editor.lineHighlightBackground": "#EDF1F8" },
});
monaco.editor.defineTheme("kodetrain-dark", {
  base: "vs-dark", inherit: true, rules: [],
  colors: { "editor.background": "#0F172C", "editorLineNumber.foreground": "#6F7C9B", "editor.lineHighlightBackground": "#1A2440" },
});

export { monaco };
