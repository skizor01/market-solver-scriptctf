# Market CTF solver

This solver exploits the missing `holding == holding_pda` check in `buy()`.

The solver program:
1. initializes the user PDA,
2. deposits 2 SOL,
3. calls `buy()` with the market CONFIG PDA supplied twice, including as `holding`.

The buy handler then interprets Config as Holding and writes the user pubkey into Config.owner.

Build with GitHub Actions using the included workflow, then download `solve.so`.
