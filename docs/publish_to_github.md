# How to publish this repository to GitHub

This guide assumes that the repository folder is already organized locally as:

- `github_results123_policy_package/`

## Before uploading

Check these three things first:

1. remove any temporary files you do not want public
2. confirm that no confidential raw data are included
3. confirm that the files under `inputs/` are only placeholders unless you explicitly want to publish data

Recommended to keep in the repository:

- `scripts/`
- `docs/`
- `data/compact/`
- `figures/main_text/`
- `README.md`
- `.gitignore`
- `requirements.txt`

Recommended to keep out unless you have cleared size and sharing issues:

- large raw CSV exports
- Word drafts
- private PDFs
- oversized generated output directories not needed for understanding the workflow

## Option 1: Upload with GitHub Desktop

1. Open GitHub Desktop.
2. Choose `File` -> `Add local repository`.
3. Select:
   - `.../github_results123_policy_package`
4. If GitHub Desktop says the folder is not yet a repository, choose `Create a repository here`.
5. Set:
   - Name: `ageing-energy-policy`
   - Description: a short article description
   - Keep the existing `README.md`
6. Review the changed files.
7. Write a first commit message such as:
   - `Initial article code and compact data package`
8. Click `Commit to main`.
9. Click `Publish repository`.
10. Choose:
   - public, if you want the paper code visible
   - private, if you want to review it first

## Option 2: Upload with terminal

Open terminal inside the repository folder:

```bash
cd "/Users/longlab/Documents/New project/github_results123_policy_package"
```

Initialize Git if needed:

```bash
git init
git add .
git commit -m "Initial article code and compact data package"
```

Create an empty repository on GitHub, then connect it:

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git branch -M main
git push -u origin main
```

## Suggested repository name

Good options:

- `ageing-energy-policy`
- `ageing-energy-policy-overton`
- `global-inequalities-ageing-energy-policy`

## Suggested short description

Code, compact data, and figure manifests for a study of global inequalities in ageing and energy policy influence.

## Suggested first public release notes

You can describe the repository as including:

- code for the main figures and supporting analyses
- compact figure source tables
- method scripts for the ageing–energy SDG framework
- supplementary analysis scripts and SI tables

## After publishing

Once the repository is online, check:

1. whether the README renders clearly
2. whether `docs/manifests/main_text_figure_manifest.md` opens correctly
3. whether the compact data directories are visible and understandable
4. whether any file should still be removed for privacy or size reasons

If you want, the next cleanup step is usually:

- add a repository license
- add a citation file
- add a short data-availability statement
