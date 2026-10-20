# Free classification provider choice

Checked October 20, 2026. The comparison uses the no-paid-services requirement. No Copilot credits were consumed and no billing settings were changed. Individual account billing details are not needed in this operational guide.

Keep Gemini as the current classifier. It has a direct structured-output API, a configured Actions secret, and successful live positive/negative tests. Narrow local rules, content-hash caching, bounded generation and automatic retries on later runs reduce dependence on an external model. Keep Google project billing disabled; a key cannot prove billing status. There is no automatic paid-model fallback or search grounding. [Google pricing](https://ai.google.dev/gemini-api/docs/pricing).

Copilot is a technically possible alternative through its supported SDK and CI authentication. It is not an unlimited inference allowance: AI credits vary with usage, are shared with other Copilot activity, and Student currently uses automatic model selection. We have not measured its news-classification capacity or quality. Adding its SDK/CLI, authentication and quota handling would introduce another integration without a demonstrated benefit for this workload. No Copilot credits were consumed for comparison and no new Copilot token was requested.

This is an operational recommendation, not a claim that Gemini is universally more accurate. If Gemini's measured reliability becomes insufficient, benchmark a bounded set of public candidates against Copilot with paid overages disabled, all tools disabled, identical relevance/date gates, explicit credential isolation and equivalent recovery tests before changing providers.

Sources: [GitHub plans](https://docs.github.com/en/copilot/get-started/plans), [AI-credit billing](https://docs.github.com/en/billing/concepts/product-billing/github-copilot-billing), [supported SDK authentication](https://docs.github.com/en/copilot/how-tos/copilot-sdk/auth/authenticate).
