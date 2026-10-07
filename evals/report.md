# P-002 vision-model selection — results

Method per `vision-model-selection.md`: three animated **build-up clips** delivered as
ordered frame sequences; exact ground truth (labels, connections, overlays, build order);
four models, one run each (`k = 1`).

## Results

| model | c1 + c3 mean recall | all-clip mean\* | cost (15 frames) | input tokens |
|---|---|---|---|---|
| **Gemma 4 31B** (`kilo/google/gemma-4-31b-it`) | **1.00** | 0.923 | **$0.0354** | 241,878 |
| **GLM 5.3 Flash** (`kilo/z-ai/glm-5.3-flash`) | **1.00** | 0.900 | $0.1433 | 787,443 |
| Gemini 3.8 Flash (`kilo/google/gemini-3.8-flash`) | **1.00** | 1.000 | $0.3384 | 307,851 |
| Muse Spark 1.3 (`kilo/meta/muse-spark-1.3`) | **1.00** | 0.900 | $0.3479 | 161,742 |

\*The **all-clip** column is shown for the record only. Clip `c2` was **confounded by a
fixture bug** — `Encoder` and `Latent` were drawn at the *same* coordinates, so the model
saw one box changing label; the one model that enumerated both (Gemini) was rewarded while
the others (reasonably) read a single box. The bug is fixed in `make_clips.py`; a
confirmatory `c2` re-run is pending.

On the **unambiguous** clips (`c1`, `c3`) **all four scored 1.00** across labels,
connections, overlays and build order. This suite **does not discriminate on quality**, so
the decision is **cost-driven**.

## Decision (pre-registered rule — cheapest within 0.10 of best)

- **Primary: `Google: Gemma 4 31B`** — ties the field on the valid clips at **~1/10 the
  cost** of Gemini/Muse. (It even leads the all-clip column among the non-perfect scores.)
- **Fallback: `Z.ai: GLM 5.3 Flash`** — a different family from the primary, next-cheapest,
  same quality band.
- Not selected: **Gemini 3.8 Flash** (best raw mean, but ~10× Gemma's cost and the same
  family as the primary) and **Muse Spark 1.3** (~10× cost, no quality gain).

## Caveats

- `k = 1`, `n = 3` clips: no variance estimate and weak discrimination.
- The `c2` fixture bug contaminated the all-clip means; `c1`/`c3` are valid and were used
  for the decision.
- Fixtures are clean synthetic renders, not real talk video.
- Cost is for a 15-frame run; it scales with segment count in real use.

## Recommendation

Adopt **Gemma 4 31B (primary)** and **GLM 5.3 Flash (fallback)** for P-002, and validate on
**real** clips during P-002 proper. If either underperforms on real figures, re-run a
corrected, harder suite (fixed `c2` plus a few adversarial clips) before re-selecting.
