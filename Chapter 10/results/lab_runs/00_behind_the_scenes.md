# Behind the scenes — issues hit & key takeaways

_A record of what it actually took to get the lab running on `claude-sonnet-4-6`, the
fixes made along the way, and the conceptual lessons each step surfaced. Updated after
the final full run (steps 3–10, exit 0); the per-step reports and
`00_comparison_quick_ratio_policy.md` in this folder are the supporting evidence._

---

## Part 1 — Engineering issues we hit (and how each was fixed)

These only surfaced by **running** the code — imports alone passed every time.

1. **`ModuleNotFoundError: No module named 'workflows.checkpointer'`.**
   `llama-index-core 0.12.x` imports `workflows.checkpointer`, which the newer
   `llama-index-workflows 2.x` had removed. First fixed by pinning the workflow engine
   to `<2` (→1.3.0); later made moot by the full 0.14 upgrade (which uses workflows 2.x
   with a compatible core).

2. **`404 not_found` on the model — twice, for different reasons.**
   The model was changed to `claude-3-7-sonnet-latest` (404), then `claude-sonnet-4-20250514`
   (404). Two root causes stacked: (a) the old `llama-index-llms-anthropic 0.7.x` ships a
   **hardcoded model registry** that predates `claude-sonnet-4-6` and rejects the name
   *client-side*, before any API call; (b) `client.models.list()` revealed the API key is
   **newer-models-only** — it has `claude-sonnet-4-6` (and opus-4-8, sonnet-4-5, …) but
   **not** the older 3.7 / 4.0 models. So downgrading the model was the wrong direction;
   the original `claude-sonnet-4-6` was right all along.

3. **Full-stack migration to the LlamaIndex 0.14 line.**
   To get `claude-sonnet-4-6` recognized natively (wrapper `>=0.11`). The old pip
   resolver kept *downgrading* because the 0.12-era OpenAI sub-packages cap `core<0.13`.
   After upgrading pip, `llama-index-agent-openai` turned out to have **no 0.14 release**
   at all — so the obsolete OpenAI helper trio (`question-gen-openai` / `program-openai` /
   `agent-openai`) was removed. Final baseline: `core 0.14.23`, `llms-anthropic 0.11.6`,
   `embeddings-openai 0.6.0`, `retrievers-bm25 0.7.1`, `workflows 2.22.1`.

4. **`SubQuestionQueryEngine` still defaults to an OpenAI question generator.**
   Even on 0.14, `from_defaults()` hard-imports `llama_index.question_gen.openai` and
   errors if absent. Fixed by passing `LLMQuestionGenerator.from_defaults()` so
   decomposition runs on Claude like every other step.

5. **`RuntimeError: no running event loop` from the agent.**
   In workflows 2.x, `FunctionAgent.run()` calls `asyncio.create_task()` synchronously
   and must be invoked *inside* a running loop, so `asyncio.run(agent.run(task))` breaks.
   Fixed by awaiting `agent.run()` inside a small coroutine.

6. **`UnicodeEncodeError: '≥'` on Windows.**
   Claude's finance answers routinely contain `≥ ≤ —`; Windows stdout defaults to cp1252,
   which can't encode them. Fixed with `sys.stdout.reconfigure(encoding="utf-8")`.

7. **The agent's retrieved chunks weren't captured.**
   `AgentOutput` exposes no `source_nodes` — the agent retrieves *inside* tool calls.
   Fixed by streaming `ToolCallResult` events and pulling chunks from each
   `tool_output.raw_output.source_nodes`.

8. **Step 5 chunks labelled `unknown`.**
   `SubQuestionQueryEngine` adds its synthesized sub-answer nodes ("Sub question: … /
   Response: …", no `file_name`, no score) to `source_nodes`. Relabelled them
   `(synthesized sub-answer)` so they aren't mistaken for retrieved document chunks.

---

## Part 2 — Key conceptual takeaways

**The big one: two orthogonal axes.** Steps 4–6 structure the *reasoning*
(route / decompose / iterate); steps 7–10 are retrieval-quality and evaluation
*add-ons* that change *what is fetched or scored*, not *how the model reasons over it*.
They are meant to **compose**, not compete — feed hybrid-retrieved, reranked chunks into
the tools a router or agent calls.

**Separate retrieval from reasoning when judging an answer.** A wrong or self-contradictory
*answer* is usually a generation artifact, not a retrieval failure — the needed facts are
almost always in the retrieved chunks (this is a tiny corpus). The router proved it on this
run: it retrieved *both* the policy (1.00 floor) and the earnings call (1.18) perfectly,
yet still tangled the firm's two thresholds — importing the *current-ratio* exception band
(current ratio `< 1.50` → Risk Committee sign-off) and mis-applying it to the *quick* ratio
in a single unstructured pass. The verdict happened to net out correct, but the reasoning
slip is plainly visible sitting on top of fully-correct retrieval.

**Per step:**
- **Step 3 (naive)** and **Step 7 (hybrid)** share the same single-pass shape: both
  answered the cross-source question correctly this run, but only as reliably as one
  sampling allows. Hybrid improves *recall*, not reasoning.
- **Step 4 (router)** commits to one tool by design, yet on a cross-source question the
  single synthesis pass has no reasoning scaffold — this run it surfaced *both* relevant
  documents and *still* conflated the quick- and current-ratio rules, reaching the right
  verdict by luck.
- **Step 5 (decomposition)** answers isolated sub-questions before synthesizing →
  prevents threshold cross-contamination → cleanest cross-source answer. Its `source_nodes`
  carry both synthesized sub-answers *and* the underlying retrieved chunks.
- **Step 6 (agent)** actively gathers the figure *and* the threshold and *resolves* the
  "use the most recent annual report" caveat (1.23 controlling, 1.18 also clears) → most
  robust, best-sourced verdict.
- **Step 7 — RRF.** Reciprocal Rank Fusion **discards** the raw cosine and BM25 scores
  (incompatible scales) and fuses by *rank*: `score(d) = Σ 1/(k + rank_d)`, with `k=60`
  smoothing so top ranks don't dominate. `mode` (list fusion) and `num_queries` (query
  fan-out) are independent — even at `num_queries=1` there are still two lists (dense +
  BM25) to fuse.
- **Step 8 — rerank.** An LLM-based reranker is a *node postprocessor*: it sits between
  retrieval and generation and trims the candidate set. The LLM **assigns** each kept doc
  a 1–10 relevance score (10 = most relevant) and omits the irrelevant ones — it is a
  judgement, not a computed distance, so it is non-deterministic.
- **Step 9 — composition.** Hybrid + rerank = the recall-then-precision pipeline of
  Figure 10.12. The *only* difference from Step 7 is the `node_postprocessors` argument.
- **Step 10 — evaluation.** Faithfulness (grounding, pass/fail) + answer relevancy
  (answer vs question) + context relevancy (chunks vs question) — the full RAG **triad**.
  Faithfulness returns pass/fail; the two relevancy evaluators return a graded 0–1 score
  (both `1.0` here).

**Tiny-corpus artifacts are not bugs.** With three short documents (the 10-K is ~3,000
chars → a *single* chunk), retrieval/rerank machinery has almost nothing to discriminate:
RRF scores all collapse to ~0.033, and Step 8 keeps only one chunk (scored 10/10) because
only one ever existed. These would spread out on a realistically sized corpus.

**LLM non-determinism.** The same step can answer differently across runs — the router
refused to rule on an earlier run (manufacturing a 1.00-vs-1.25 *quick-ratio* conflict) yet
reached a correct, if muddled, verdict on this one. Describe *tendencies*, not a single
sampled answer as definitive.

---

## Part 3 — What the final run actually showed

The shared question — *"Does Acme's Q3 quick ratio satisfy the firm's risk policy?"* —
through every retrieval pattern. **Ground truth:** Q3 quick ratio `1.18 ≥ 1.00` policy
floor → **yes, it satisfies**, with caveats (declining trend; the policy says use the
*most recent annual report*, whose year-end `1.23` also passes).

| Step | Verdict | Correct? | Sources touched | Note |
|------|---------|:--------:|-----------------|------|
| 3 — Naive | "Yes, but only marginally" | ✅ | 3 | clean; pulled the year-end 1.23 and the 41% concentration flag |
| 4 — Router | "No hard block" (hedged) | ✅ | 2 | right verdict, shakiest path: conflated quick- vs current-ratio rules, then stalled on sourcing |
| 5 — Decomposition | "Yes, satisfies" | ✅ | 4 | cleanest & most concise; isolation avoided the threshold mix-up |
| 6 — Agent | "✅ PASS" | ✅ | 3 | most complete & best-sourced; used 1.23 as controlling, separated covenant vs quick ratio |
| 7 — Hybrid | "Yes, warrants monitoring" | ✅ | 3 | correct; RRF collapsed all three chunks to 0.033 |
| 9 — Hybrid + rerank | "✅ Passes" | ✅ | 3 | correct and clean; best-ordered retrieval (9/9/6) |

**The headline finding:** this run, **all six patterns reached the correct verdict** — the
router included. So the result no longer separates them into pass/fail; it separates them
by *reasoning quality*. The most instructive case is the router: handed both facts, it
still conflated the **current-ratio** rule (`< 1.50` → exception) with the **quick-ratio**
floor (`1.00`), manufactured a "1.00–1.50 quick ratio needs an exception" band that is
nowhere in the policy, and only backed into the right answer because Acme satisfied both
conditions anyway. That same threshold confusion is the recurring weak spot of the
single-pass steps (3, 4, 7, 9); on an earlier run it tipped the router into an outright
refusal to rule. The **structured-reasoning** steps handled it cleanly — decomposition (5)
by answering isolated sub-questions, and the agent (6) by explicitly separating the
covenant from the quick-ratio rule and resolving the sourcing caveat.

**Correctness here is the luck of the draw — that is the real lesson.** Because each step
is a single non-deterministic pass, the un-scaffolded patterns (3, 4, 7, 9) were right
*this* time but carry no guarantee; the same router reasoning that netted out correct here
produced a wrong answer on a prior run. The self-correcting agent's value is converting a
right-on-a-good-day answer into a *repeatably* right one by checking its own sufficiency
before it commits.

**Retrieval quality ≠ reasoning quality — demonstrated.** The router had perfect retrieval
for this question (both the 1.00 policy floor and the 1.18 Q3 ratio in context) and still
tangled its reasoning; conversely Step 9, with the best-ordered retrieval of the run
(rerank scored the policy and call 9/10, the 10-K 6/10), reasoned cleanly. Good chunks
raise the odds of a good answer but do not lock it in — which is exactly why the retrieval
add-ons (7–10) and the reasoning patterns (4–6) are complementary, not substitutes.

**Sources touched does not predict answer quality:** naive / hybrid / hybrid+rerank and the
agent pulled all three documents; the router pulled the two that matter and was the
shakiest; decomposition's pool was its synthesized sub-answers plus the underlying chunks.
The router saw enough and still tangled them, while the agent turned the same breadth into
the most rigorous verdict — evidence that *how* the model reasons over retrieved facts, not
*how many* it sees, is what determines the answer.
