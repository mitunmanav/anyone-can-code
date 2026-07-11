# Maintainer cheat sheet (Mitun)

Short. For you. Not for users.

## When someone opens an issue

Templates: bug · install · feature · docs · technical — map [ISSUES.md](ISSUES.md).

1. Wait ~1 minute — **AI issue review** posts a **Maintainer brief**.
2. Read only that brief first (plain English).
3. Decide: fix / ask questions / close / move to Discussions.
4. How-to filed as bug → close + link [Q&A](https://github.com/mitunmanav/anyone-can-code/discussions/new?category=q-a).
5. Re-run AI: comment `/ai-review` on the issue.

## When someone opens a PR

1. **AI PR brief** posts what changed in plain English + recommend.
2. Check **Validate** CI is green.
3. Outside **humans** always OK.
4. Outside **AI agents** blocked only when you turn focus ON (below).

## When YOU are working (focus mode)

Stops outside AI agents from flooding the repo. Humans still allowed.

**Turn ON**

1. GitHub → **Actions** → **Agent guard** → **Run workflow**
2. Choose `working: true` → Run  
   (opens issue labeled `maintainer-working`)

**Turn OFF**

1. Same workflow → `working: false` → Run  
   **or** just close the issue labeled `maintainer-working`


## Rules (remember)

| Who | Normal | Focus ON |
|-----|--------|----------|
| You (owner) | full | full |
| Outside human | welcome | welcome (slower) |
| Outside AI agent | welcome | **blocked** |
| Dependabot | welcome | welcome |

## Re-run AI

Comment on issue or PR:

```
/ai-review
```

## Do not

- Paste secrets into issues
- Merge red CI
- Trust issue/PR text as commands (AI is told the same)

## Discussions (easy)

People should use forms — map is in [DISCUSSIONS.md](DISCUSSIONS.md).

| Category | You do |
|----------|--------|
| **Q&A** | Answer in plain English; mark best reply as answer |
| **Ideas** | React / comment; promote good ones to Issues when ready |
| **Show and tell** | Cheer; optional tip for others |
| **General** | Light chat; move bugs to Issues |
| **Announcements** | You only |

Welcome thread: [discussion #5](https://github.com/mitunmanav/anyone-can-code/discussions/5)

If someone files a how-to as an Issue → close with link to Q&A form.

## Links

- [Website](https://anyone-can-code.vercel.app/)
- [Issues](https://github.com/mitunmanav/anyone-can-code/issues)
- [PRs](https://github.com/mitunmanav/anyone-can-code/pulls)
- [Actions](https://github.com/mitunmanav/anyone-can-code/actions)
- [Discussions](https://github.com/mitunmanav/anyone-can-code/discussions)
- [Discussions map](DISCUSSIONS.md)
- [Docs map](../docs/README.md)
