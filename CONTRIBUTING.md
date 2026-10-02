# Team workflow

1. Pull the latest `main`: `git pull --ff-only`.
2. Create a branch: `git switch -c feat/short-description`.
3. Build a small working slice. Run the relevant application checks once added.
4. Run `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check.ps1`.
5. Commit: `git add <files>` then `git commit -m "Add ..."`.
6. Push: `git push -u origin HEAD` and open a pull request.
7. Have a teammate review, then merge and sync `main`.

For a tiny hackathon team, agree together if direct commits to `main` are faster.
Keep `main` runnable and coordinate before editing the same files.

Do not commit `.env`, credentials, personal datasets, or generated dependencies.
Commit dependency lockfiles when a package manager is chosen.
Keep each issue scoped to a deliverable and assign one owner.
