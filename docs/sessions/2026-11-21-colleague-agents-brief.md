# Session brief: designing the colleague agents

Session of 2026-11-21. Read this before designing the full set of colleague
agents for the 1+Claude system. It records what was decided, what was built,
what went wrong, and what the outside record shows about how others build agent
teams.

Each line is labelled **Blake** (his decision or statement) or **Claude**
(a finding or a suggestion he has not adopted).

---

## 1. The objective

- **Blake:** the system is a simulated workgroup anchored by real humans.
  Agents are colleagues tied to people, not generic functions.
- **Blake:** his human judgment governs; agents advise, he decides.

## 2. What exists now (merged to main, PR #16)

| Agent | Role | Model |
|---|---|---|
| snowflake | Advisor: how would Snowflake Inc. proceed. Also keeps the org chart, the contract registry and the review queue | opus |
| salesforce | Advisor: how would Salesforce Inc. proceed | opus |
| chablis | Data acquisition with provenance | sonnet |
| data-simplifier | Cleanup of Python/SQL after changes; behavior and stored data preserved | opus |
| experience-simplifier | Cleanup of TS/React/HTML/CSS after changes | opus |

Key files: `snowflake/ORG.md` (agent roster with a **human anchor** column,
all Blake today), `snowflake/CONTRACTS.md` (frozen interfaces C1–C3, each with
a human owner), `snowflake/REVIEW_QUEUE.md` (what agents may not change
themselves), `CLAUDE.md` (routing and the platform panel).

## 3. Patterns established this session (reuse them)

1. **Vendor-perspective advisor.** **Blake:** an agent named for a company
   answers "how would that company proceed", fed with its published best
   practices. It is not a platform commitment. Every answer carries
   *when this vendor is not the answer* and *what the vendor gains*.
2. **Platform panel.** Two vendor advisors get the same brief and answer
   independently. The main session compares them and adds the
   no-new-platform option. Blake decides.
3. **Two layers, one frozen contract.** **Blake:** split the code agents into
   presentation and data. Keep the TypeScript/React standards and add
   Python — "create both capabilities", never swap one for the other. The
   handoff between the layers is frozen for both agents.
4. **Escalate, don't change.** Anything structural (schema, migrations, file
   formats, a contract) goes to the review queue. Snowflake advises; the human
   owner decides.
5. **Learning path.** Each advisor has a doctrine distilled from its sources,
   a 30-day path run against real systems, a findings-only log and a
   progress file.
6. **Model tiers.** **Blake's rule:** pay for the higher model where an
   undetected error costs more than the tokens. Here that means advisors and
   the panel synthesis on Opus. Daily lessons, mechanical edits and merges
   can run on Sonnet or Haiku.

## 4. What the outside record shows (Claude's research)

- **Common shape:** one human principal, one coordinator (often called
  "chief of staff"), domain leads under it, short-lived workers below.
  Hierarchies stay at three levels or fewer.
  ([Anthropic, multi-agent research](https://www.anthropic.com/engineering/multi-agent-research-system);
  [Coinbase CEO's setup](https://www.thestateofai.com/news/coinbase-brian-armstrong-ai-chief-of-staff-agent))
- **Roles that work in production:** writer, reviewer (with a clean
  context), advisor (stronger model consulted by a cheaper one) and manager.
  Writes stay single-threaded; extra agents add judgment, not edits.
  ([Cognition, Apr 2026](https://cognition.com/blog/multi-agents-working))
- **Manager vs handoff:** manager when one agent should keep ownership of the
  answer; handoff when a specialist should take over.
  ([OpenAI orchestration guide](https://developers.openai.com/api/docs/guides/agents/orchestration))
- **Boris Cherny's setup (creator of Claude Code):** agents anchored to
  *tasks*, not personas. Parallel sessions, each in its own git worktree;
  one team-owned CLAUDE.md that grows a line whenever Claude errs.
  His published plugins are in
  [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official).
- **Cost:** multi-agent systems use roughly 15× the tokens of a chat
  (Anthropic). Count it in every design.
- **Claude's read of the gap:** none of the published setups anchor agents
  to real people. That is the distinctive part of Blake's design, and the
  hardest: consent, keeping each person's agent current, and authority limits.

## 5. Mistakes this session; don't repeat them

- **"Snowflake" means two things.** Claude read Blake's view that Snowflake
  Inc. will grow as a decision to use it as the data layer, wrote that into
  the agent, and had to reverse it. Ask, or read the context. A judgment about
  a company's prospects is not a platform commitment.
- **Don't substitute when asked to extend.** Claude proposed swapping the
  upstream TS/React standards for Python; Blake wanted both.
- **Check overrides against hard limits.** The first data-simplifier let a
  team CLAUDE.md override its safety rules. Fixed: CLAUDE.md overrides style,
  not hard limits.
- **Merging to main needs Blake's explicit sign-off** in this environment.
  Push a branch, open the PR, and ask him to merge.

## 6. Tooling notes

- GitHub profile pages are robots-blocked to fetch; public repos clone
  fine through the session's git proxy.
- In cloud sessions, `gh pr create` fails (GraphQL is blocked). Open PRs with
  `gh api repos/<owner>/<repo>/pulls -f title=… -f head=… -f base=… -F body=@file`.
- Push access comes from `add_repo` with `access: push`; that clone lives at
  `/home/claude/claude1`.

## 7. Open questions for the design session (Blake's to answer)

1. Which real people anchor which lanes, and has each agreed to take part?
2. Does the roster need a coordinator (chief-of-staff) agent above the
   advisors, or does Blake stay the coordinator?
3. Which other vendor or practitioner lenses belong on panels?
4. What may each agent write, and what must route through the review queue?
5. Naming convention: company-named advisors (Snowflake, Salesforce) and
   personal names (Chablis) — keep both, or settle on one?

## 8. Start the new session with

- Blake's four fields: OBJECTIVE / ALREADY TRIED / OFF THE TABLE / DELIVERABLE.
- `snowflake/ORG.md` and `snowflake/CONTRACTS.md` as the current state.
- This brief, sections 3–5.
