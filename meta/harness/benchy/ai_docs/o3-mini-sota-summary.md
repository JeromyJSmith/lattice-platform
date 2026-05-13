# SOTA Reasoning Model

| **Model**       | **Pricing Input (1m)**  | **Pricing Output (1m)** | **Context Window** | **Max Output Tokens** | **Reasoning Effort Control**                    | **Speed** |
| --------------- | ----------------------- | ----------------------- | ------------------ | --------------------- | ----------------------------------------------- | --------- |
| **o3‑mini**     | $1.10 / $0.55 (cache)   | $4.40                   | 200K ⭐             | 100K ⭐                | reasoning_effort: "low" \| "medium" \| "high" ⭐ | Fastest ⭐ |
| **o1**          | $15.00 / $7.50 (cache)  | $60.00                  | 200K ⭐             | 100K ⭐                | reasoning_effort: "low" \| "medium" \| "high" ⭐ | Fast      |
| **deepseek‑r1** | $0.14 / $0.55 (cache) ⭐ | $2.19 ⭐                 | 64K                | 8K                    | N/A                                             | Moderate  |

---

## Insights

- ⭐️ o3-mini is ~8x cheaper than o1.
- ⭐️ o3-mini is ~8x more expensive than deepseek-r1.
- ⭐️ o3-mini maintains o1's 200k context window
- ⭐️ o3-mini maintains o1's 100k max output tokens
- ⭐️ o3-mini provides SOTA instruction following.
- o3-mini specializes in code, math, science and large context tasks.
- o3-mini "high" outperforms o1 on nearly every vibe check, and benchmark
- o3-mini is the fastest model especially in low reasoning effort.
- o3-mini enables reasoning effort control
- o3-mini has ~4x larger context window than deepseek-r1
- o3-mini has ~12x more output tokens than deepseek-r1
- o3-mini, has support for structured outputs and tool calling.

## One Line Summary
- **o3-mini is o1, but 0 to 15% better, at an 8th of the price, with all the capabilities of o1 built to help you accomplish coding, math, reasoning, planning and large context tasks.**
- **o1 is the previous SOTA model, but o3-mini is 8x cheaper and 15% better.**
- **deepseek-r1 is a close second, that boasts an incredible 16x price reduction over o1 and 8x reduction over o3-mini. deepseek-r1's limitation lie in its 64k context window and 8k max output tokens. It also underperforms o3-mini in high reasoning effort. The deepseek api has also been completely hammered and is effectively unusable.**