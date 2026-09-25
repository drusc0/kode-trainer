# Frontend tooling

**Status:** adopted 2026-09-25 · **Scope:** `frontend/` (React 18 + Vite 8 SPA, served by nginx)

| Job | Tool | Command |
|---|---|---|
| Package manager | [pnpm](https://pnpm.io/) 12 via corepack (pinned in `packageManager`) | `corepack pnpm install` (or `corepack enable` once, then `pnpm …`) |
| Lint + format + import sorting | [Biome](https://biomejs.dev/) 2 | `pnpm lint` (check) · `pnpm format` (write) |
| Type checking | `tsc --noEmit` (unchanged, part of `pnpm build`) | `pnpm exec tsc --noEmit` |
| Tests | [Vitest](https://vitest.dev/) 5 + Testing Library + jsdom | `pnpm test` |

From the repo root, `make lint` and `make test` run all of these (plus the backend's checks).

## Why these

### pnpm, not npm, Bun or Yarn
The actual problem was reproducibility. No lockfile was committed, and the Dockerfile ran `npm install` against `^` ranges, so every image could ship different dependency versions. Any package manager with a committed lockfile fixes that. pnpm was chosen for what it adds on top:

- **Strict `node_modules`.** Code can only import packages it declares. npm's hoisting lets undeclared ("phantom") imports work locally and then break later.
- **Fast installs and a shared content-addressed store**, which saves disk across projects and worktrees.
- **Build scripts off by default.** Dependencies can't run install scripts unless explicitly allowed, which closes a common supply-chain attack path. None are allowed today: Vite 8 bundles with Rolldown and no longer needs esbuild's install script. If a future dependency needs one, allow it by name under `allowBuilds` in a `pnpm-workspace.yaml`, and copy that file in the Dockerfile.
- **Minimum release age.** pnpm 12 refuses versions published less than a day ago, even when they're already in the lockfile (`ERR_PNPM_MINIMUM_RELEASE_AGE_VIOLATION`). That's why Vitest resolves to 5.0.1 rather than 5.0.2, which was released on upgrade day. Wait out the cutoff rather than relaxing the policy. If a brand-new version was already locked, `pnpm clean --lockfile && pnpm install` re-resolves under the policy.
- **Pinned through corepack.** The `packageManager` field pins the exact pnpm version, and Node 24's corepack fetches it, so there's nothing to install globally.

Rejected alternatives:
- **npm** works, but it's the slowest and hoists everything. Staying on it would still have required fixing the lockfile.
- **Bun** has the fastest installs and a built-in test runner, but it's a whole runtime. This app only uses Node at *build* time, because nginx serves static files. Vite and Vitest target Node semantics, so adopting Bun buys install speed at the cost of compatibility risk. Revisit only if the frontend ever gets a JS server.
- **Yarn Berry** has a strict and fast Plug'n'Play mode, but PnP breaks some tooling, and the industry has largely moved to pnpm for this niche.

### Biome, not ESLint + Prettier
- **One tool, one config (`biome.json`), no plugins.** It's the JS equivalent of the backend's ruff, and it checks and formats the whole app in about 15 ms.
- It covers the rules that matter for React: hooks dependencies (`useExhaustiveDependencies`), a11y (button types, ARIA, semantics), correctness, and suspicious patterns. It also lints and formats CSS.
- **Trade-off accepted:** ESLint has a larger rule ecosystem, notably *type-aware* rules such as `@typescript-eslint/no-floating-promises` that need the TypeScript compiler. If unawaited API calls in `api.ts` ever become a real bug source, add ESLint with only typescript-eslint's type-aware rules next to Biome, rather than replacing it.
- Style matches what the code already used: 2 spaces, double quotes, semicolons, 120 columns (same as ruff).
- Rules turned off, with reasons:
  - **`noArrayIndexKey`:** every indexed list here (examples, hints, test cases, result cells) is positional with no stable id, so the index *is* the identity.
  - **`noNonNullAssertion`:** `!` is used deliberately where an invariant holds (the `#root` element, a session that the router guarantees).
  - **`noDescendingSpecificity`:** component-scoped CSS such as `.md td` and `.ptable td` never nest, so its findings are noise.
- Every other deliberate deviation is an inline `biome-ignore` with a reason. These replaced the old `eslint-disable` comments that referred to an ESLint that was never installed.
- Real fixes it drove:
  - Every `<button>` now has an explicit `type="button"`.
  - The result strip's `aria-label` now has `role="img"`, so screen readers actually announce it.

### Vitest, not Jest
- It reuses `vite.config.ts` (same JSX transform, aliases and `import.meta.glob`), so there's no second Babel/ts-jest pipeline to keep in sync. The config is just `test: { environment: "jsdom" }`.
- It's Jest-compatible (`describe`, `it`, `expect`) and fast in watch mode (`pnpm exec vitest`).
- Vitest's major version tracks Vite's (Vitest 5 supports Vite 6.4 to 8), so upgrade both together. `@vitejs/plugin-react` 6 requires Vite 8.
- Current tests:
  - `components/ui.test.tsx` checks that the result strip renders one cell per test, compresses long runs to 60 cells without ever hiding a failure, and announces the pass count, plus the verdict → colour mapping.
  - `content/patterns.test.ts` checks that every pattern has a non-empty guide. `patternBody` silently falls back to `""`, so a renamed `.md` would otherwise ship a blank page.

## Consequences and follow-ups
- The Docker build now runs `node:24-alpine` (Node 20 reached end-of-life in April 2026) and `pnpm install --frozen-lockfile`. A new `.dockerignore` stops the host's `node_modules` (macOS binaries) from being copied over the container's.
- The first `biome format` reformatted most files, `styles.css` especially. That's a one-time diff.
- Monaco is code-split: `WorkspacePage` is lazy-loaded in `App.tsx` and imports `monaco.ts` itself, so only `/problems/:slug` downloads the editor chunk. Keep `monaco.ts` out of eagerly loaded modules, or it lands back in the entry chunk.
