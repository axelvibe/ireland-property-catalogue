# The Pipeline — How Agents Hand Off Work

```
Researcher → Designer → Maker → Communicator → Manager
```

Each agent's output becomes the next agent's input. The chain is unbroken.

| Step | Agent | Produces | Consumes |
|---|---|---|---|
| 1 | 🔵 Researcher | `agents/01-researcher.md` — market research brief | Live market, CSO/PSRA data, Telegram listings |
| 2 | 🟣 Designer | `agents/02-designer.md` — solution design spec | Researcher's brief |
| 3 | 🟢 Maker | `index.html` — working single-file chatbot | Designer's spec |
| 4 | 🔴 Communicator | `agents/04-communicator.md` — brand & GTM pack | Maker's product |
| 5 | 🟡 Manager | `agents/05-manager.md` — executive summary | All four handoffs |

The live product itself shows the chain in its sidebar: **Researcher → Designer → Maker → Communicator → Manager — all online.**
