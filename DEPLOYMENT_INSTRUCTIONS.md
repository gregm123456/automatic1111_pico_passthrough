Creating the GitHub repository and pushing from local

I cannot create the repository on your GitHub account because this environment doesn't have your credentials or access to GitHub's API on your behalf. Follow one of these methods locally.

1) Using GitHub CLI (recommended):

```bash
# Install GitHub CLI: https://cli.github.com/
gh auth login
gh repo create gregm123456/automatic1111_pico_passthrough --public --source=. --remote=origin --push
```

2) Using curl + Personal Access Token (PAT):

```bash
export GITHUB_TOKEN=ghp_xxx-your-token-here
curl -H "Authorization: token $GITHUB_TOKEN" \
  -d '{"name":"automatic1111_pico_passthrough","private":false}' \
  https://api.github.com/user/repos
git remote add origin https://github.com/gregm123456/automatic1111_pico_passthrough.git
git branch -M main
git push -u origin main
```

3) Manual creation via GitHub web UI:
- Create a new repository named `automatic1111_pico_passthrough` under your account.
- Do not initialize with README/license (we already have them locally).
- Follow the instructions shown after creation to push an existing repository:

```bash
git remote add origin https://github.com/gregm123456/automatic1111_pico_passthrough.git
git branch -M main
git push -u origin main
```

If you want, you can automate repository creation in CI using a machine user or GitHub App, but be careful with token permissions.
