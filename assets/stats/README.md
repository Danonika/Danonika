# About these statistics

The cards are refreshed daily by GitHub Actions using the read-only `STATS_TOKEN`
secret. Only aggregate numbers and SVG cards are published. Private repository
names, paths, commit messages, and source code are never published by the workflow.

## Code changes

**+ lines added / − lines deleted**, over the past 12 months. The exact date range
appears on the card. Counts come from GitHub's commit `additions` and `deletions`
fields, filtered to commits associated with Danonika's GitHub author identity.

- Includes accessible public and private repositories where Danonika is an owner,
  collaborator, or organization member. Token access determines private coverage.
- Counts commits reachable from each non-fork repository's default branch.
  Unmerged branches and repositories the token cannot access are outside the scope.
- Paginates both repositories and commit histories. Identical commit hashes count
  once, and merge commits are excluded to avoid counting their changes twice.
- These are changed text lines, including documentation, configuration, generated
  files, and bundled dependencies reported by GitHub. They are not a measure of
  unique source code, productivity, or current project size. Editing the same line
  repeatedly can contribute repeatedly to the totals.
- GitHub's commit history date filter defines the time window. If any API query
  fails, the workflow preserves the previous cards instead of publishing partial
  totals. Accounts or commit emails GitHub cannot associate with the author are
  not included.

Aggregate totals and the exact timestamps are in [code-changes.json](code-changes.json).
See [GitHub's Commit API reference](https://docs.github.com/en/graphql/reference/commits).

## Activity

The activity card uses GitHub Stats Extended through the pinned GitHub Readme Stats
Action. It includes accessible private activity and all-time contributions.
[Calendar artwork](../../calendar-art/README.md) is included in contribution totals.
