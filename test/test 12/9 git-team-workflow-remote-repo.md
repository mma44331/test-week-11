# Lab: Git Team Workflow with Remote Repositories

**Duration:** 90–120 minutes  
**Difficulty:** Intermediate  
**Prerequisites:** Basic terminal navigation, text editor familiarity

---

## Overview

This lab teaches you how to work like a professional software team using Git with a remote repository (GitHub, GitLab, or Bitbucket). You'll learn to initialize a local repository, connect it to a remote server, verify everything works at each step, and execute a realistic branching/merging workflow used in production environments.

**Key Learning Outcomes:**
- Understand the relationship between local and remote repositories
- Master upstream tracking and branch management
- Execute a professional branching strategy (main/dev/feature/*)
- Debug common push/pull failures
- Verify system correctness at every stage

---

## Part 0: Mental Model & Pre-Check

### Understanding the Git Architecture

Before diving into commands, you need to understand the three-layer system you're working with:

#### **1. Local Repository (.git directory)**
- Lives on your machine in the `.git` folder
- Contains all commits, branches, staging area, and history
- Completely independent—works offline
- Your "source of truth" until you push

#### **2. Remote Repository (server copy)**
- Lives on GitHub/GitLab/Bitbucket servers
- Acts as the team's shared source of truth
- Receives pushes, serves pulls
- Does NOT automatically sync with your local repo

#### **3. Remote Name "origin"**
- A nickname for the remote repository URL
- Convention: the primary remote is called "origin"
- You can have multiple remotes (e.g., "upstream", "fork")
- Just a pointer—changing the name doesn't change the server

#### **4. Upstream Tracking**
- A link between a local branch and a remote branch
- Example: local `main` tracks `origin/main`
- Enables simple `git push` and `git pull` without specifying destination
- **Critical:** Without tracking, Git doesn't know where to push

**Mental Model Summary:**
```
Your Computer                    Remote Server
┌─────────────────┐             ┌──────────────┐
│ Local Repo      │             │ Remote Repo  │
│ (.git folder)   │   push →    │ (GitHub)     │
│                 │   ← pull    │              │
│ main branch ────┼─tracking──→ │ origin/main  │
└─────────────────┘             └──────────────┘
```

### Pre-Check: Verify Your Environment

Run these commands to ensure you're ready:

```bash
git --version
```

**Expected output:** `git version 2.x.x` or higher

```bash
pwd
```

**Expected output:** Your current directory path (you should know where you are)

```bash
ls
```

**Expected output:** Contents of current directory (verify you can list files)

**If any command fails:** Install Git from [git-scm.com](https://git-scm.com) or consult your system administrator.

---

## Part 1: Create Project Folder & Initialize Local Repository

### Step 1.1: Create Project Folder

**Commands:**
```bash
mkdir git-team-lab
cd git-team-lab
```

**What it does:**
- `mkdir git-team-lab`: Creates a new directory named "git-team-lab"
- `cd git-team-lab`: Changes your current directory into the new folder

**Why it's needed:**
- Git repositories are folder-based; you need a dedicated project folder
- Keeps your work organized and isolated from other projects

**What breaks if you skip it:**
- You'll initialize Git in the wrong directory (potentially your home folder)
- Risk mixing project files with system files

**Verification:**
```bash
pwd
```

**What to look for:**
- Output should end with `/git-team-lab`
- Example: `/Users/yourname/git-team-lab` or `/home/yourname/git-team-lab`

```bash
ls -a
```

**What to look for:**
- Should show only `.` and `..` (empty directory)
- No `.git` folder yet (we haven't initialized Git)

---

### Step 1.2: Initialize Git Repository

**Command:**
```bash
git init
```

**What it does:**
- Creates a hidden `.git` directory in the current folder
- Initializes the Git database (object store, refs, config)
- Makes this folder a Git repository

**Why it's needed:**
- Without `.git`, Git commands won't work (Git won't recognize this as a repo)
- The `.git` folder stores all commits, branches, staging area, and configuration

**What's inside `.git`:**
- `objects/`: All file contents and commits (stored as hashes)
- `refs/heads/`: Branch pointers (e.g., `main`, `dev`)
- `HEAD`: Points to your current branch
- `config`: Repository-specific settings
- `index`: Staging area (tracks what will be committed next)

**What breaks if you skip it:**
- Every Git command will fail with "fatal: not a git repository"

**Verification:**
```bash
ls -a
```

**What to look for:**
- Must see `.git` directory in the output
- Example output: `.  ..  .git`

```bash
git status
```

**What to look for:**
- Output: `On branch main` (or `master` on older Git versions)
- "No commits yet"
- "nothing to commit"
- **This proves Git is initialized and working**

---

### Step 1.3: Create Baseline Files

**Commands:**
```bash
cat > README.md << 'EOF'
# Git Team Lab

This project demonstrates professional Git workflow with remote repositories.

## Team Workflow
- `main`: Stable production-ready code
- `dev`: Integration branch for testing
- `feature/*`: Individual feature branches

## Setup
See lab instructions for complete setup guide.
EOF
```

```bash
cat > .gitignore << 'EOF'
# macOS system files
.DS_Store
.AppleDouble
.LSOverride

# Node.js dependencies
node_modules/
npm-debug.log*

# Environment variables (NEVER commit secrets)
.env
.env.local
.env.*.local

# IDE settings
.vscode/
.idea/
*.swp
*.swo

# Build outputs
dist/
build/
*.log
EOF
```

**What it does:**
- Creates `README.md`: Project documentation (describes purpose and workflow)
- Creates `.gitignore`: Tells Git which files to ignore (never track)

**Why it's needed:**
- **README.md**: Every professional project needs documentation
- **.gitignore**: Prevents committing:
  - System junk (`.DS_Store` on macOS)
  - Dependencies (can be reinstalled via `package.json`)
  - Secrets (`.env` files with API keys, passwords)
  - Build artifacts (generated files)

**What breaks if you skip it:**
- Without `.gitignore`: You'll accidentally commit secrets, huge `node_modules/` folders, or system files
- **Security risk:** Committed secrets can be stolen even after deletion (Git history persists)
- **Repository bloat:** Large files make cloning slow

**Verification:**
```bash
cat .gitignore
```

**What to look for:**
- Should display the ignore patterns you just created
- Verify `.env` is listed (critical for security)

```bash
ls -a
```

**What to look for:**
- Should see: `.git`, `README.md`, `.gitignore`

---

### Step 1.4: First Commit

**Commands:**
```bash
git add .
```

**What it does:**
- Stages all files in the current directory (`.` means "everything here")
- Moves files from "untracked" to "staged" (ready to commit)
- Updates the staging area (`.git/index`)

**Why it's needed:**
- Git uses a two-step process: stage → commit
- Staging lets you choose exactly what goes into each commit
- Allows partial commits (stage only some changes)

**Verification (before committing):**
```bash
git status
```

**What to look for:**
- "Changes to be committed:" section (green text)
- Should list: `README.md` and `.gitignore`
- **This proves files are staged**

---

**Command:**
```bash
git commit -m "Initial commit: Add README and gitignore"
```

**What it does:**
- Creates a permanent snapshot (commit) of staged files
- Stores commit in `.git/objects/` with a unique hash (SHA-1)
- Moves `main` branch pointer to this new commit
- `-m`: Specifies commit message inline

**Why it's needed:**
- Commits are the fundamental unit of Git history
- Without commits, you have no history to push
- Good commit messages document *why* changes were made

**What breaks if you skip it:**
- No history exists → nothing to push to remote
- Can't track changes or revert mistakes

**Verification:**
```bash
git log --oneline --decorate --graph -n 5
```

**What to look for:**
- One commit with your message: "Initial commit: Add README and gitignore"
- `(HEAD -> main)`: Shows you're on `main` branch and it points to this commit
- A 7-character hash (e.g., `a1b2c3d`)
- **This proves the commit exists and `main` points to it**

```bash
git status
```

**What to look for:**
- "nothing to commit, working tree clean"
- **This proves all changes are committed (no pending work)**

---

## Part 2: Create Remote Repository & Link Local to Remote

### Step 2.1: Create Remote Repository on GitHub/GitLab/Bitbucket

**Instructions (choose your platform):**

#### **GitHub:**
1. Go to [github.com](https://github.com) and log in
2. Click the `+` icon (top right) → "New repository"
3. Repository name: `git-team-lab`
4. **CRITICAL:** Do NOT check "Initialize this repository with a README"
   - **Why:** Your local repo already has a README and commits
   - **What breaks:** If remote has commits, first push will fail (divergent histories)
5. Leave "Add .gitignore" and "Choose a license" as "None"
6. Click "Create repository"
7. Copy the repository URL:
   - **HTTPS:** `https://github.com/YOUR_USERNAME/git-team-lab.git`
   - **SSH:** `git@github.com:YOUR_USERNAME/git-team-lab.git`


**URL Format:**
- Replace `<REMOTE_URL>` in the next steps with your actual URL
- Example: `https://github.com/johndoe/git-team-lab.git`

---

### Step 2.2: Add Remote to Local Repository

**Command:**
```bash
git remote add origin <REMOTE_URL>
```

**Example:**
```bash
git remote add origin https://github.com/johndoe/git-team-lab.git
```

**What it does:**
- Registers a remote repository with the nickname "origin"
- Stores the URL in `.git/config`
- Does NOT transfer any data (just saves the address)

**Why it's needed:**
- Git needs to know where to push/pull
- "origin" is the conventional name for the primary remote
- Without this, `git push` fails with "No configured push destination"

**What breaks if you skip it:**
- `git push` fails: "fatal: No configured push destination"
- Git has no idea where to send your commits

**Verification:**
```bash
git remote -v
```

**What to look for:**
- Two lines (fetch and push URLs):
  ```
  origin  https://github.com/johndoe/git-team-lab.git (fetch)
  origin  https://github.com/johndoe/git-team-lab.git (push)
  ```
- **fetch:** URL used for `git pull` and `git fetch`
- **push:** URL used for `git push`
- Usually identical unless you have a fork setup
- **This proves the remote is registered correctly**

---

### Step 2.3: Ensure Correct Default Branch Name

**Command:**
```bash
git branch
```

**What to look for:**
- Output: `* main` (preferred modern convention)
- OR: `* master` (older default on Git < 2.28)

**If you see `master` and want to rename to `main`:**

```bash
git branch -M main
```

**What it does:**
- `-M`: Force-renames the current branch to "main"
- Updates `.git/refs/heads/` (deletes `master`, creates `main`)
- Moves `HEAD` to point to `main`

**Why it's needed:**
- Modern convention: GitHub/GitLab default to `main`
- Mismatch causes confusion:
  - Local: `master`
  - Remote: `main`
  - Push fails or creates two separate branches

**What breaks if you skip it:**
- First push might create `origin/master` instead of `origin/main`
- Team expects `main`, but you're working on `master`
- Requires manual branch reconciliation

**Verification:**
```bash
git branch
```

**What to look for:**
- Output: `* main`
- **This proves you're on the correct branch**

---

### Step 2.4: First Push & Set Upstream Tracking

**Command:**
```bash
git push -u origin main
```

**What it does:**
- `push`: Sends local `main` commits to remote `origin`
- `-u` (or `--set-upstream`): Creates tracking relationship
  - Links local `main` to `origin/main`
  - Enables future `git push` without specifying destination
- Uploads commit objects, trees, and blobs to remote server

**Why it's needed:**
- Transfers your local commits to the remote (makes them visible on GitHub)
- Sets up tracking so future pushes are simpler
- Without `-u`, every push requires `git push origin main` (verbose)

**What breaks if you skip it:**
- Your code stays local (team can't see it)
- No backup exists (if your machine fails, work is lost)
- Future `git push` fails: "The current branch main has no upstream branch"

**Expected output:**
```
Enumerating objects: 3, done.
Counting objects: 100% (3/3), done.
Delta compression using up to 8 threads
Compressing objects: 100% (2/2), done.
Writing objects: 100% (3/3), 320 bytes | 320.00 KiB/s, done.
Total 3 (delta 0), reused 0 (delta 0)
To https://github.com/johndoe/git-team-lab.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

**Key line:** `Branch 'main' set up to track remote branch 'main' from 'origin'.`

---

**Verification:**

```bash
git branch -vv
```

**What to look for:**
- Output: `* main a1b2c3d [origin/main] Initial commit: Add README and gitignore`
- **Breakdown:**
  - `*`: Current branch
  - `main`: Branch name
  - `a1b2c3d`: Latest commit hash
  - `[origin/main]`: Upstream tracking (local `main` tracks `origin/main`)
- **This proves upstream tracking is configured**

```bash
git branch -r
```

**What to look for:**
- Output: `origin/main`
- **This lists remote branches Git knows about**
- Proves `origin/main` exists on the server

```bash
git log --oneline --decorate --graph -n 5
```

**What to look for:**
- Output: `* a1b2c3d (HEAD -> main, origin/main) Initial commit: Add README and gitignore`
- `(HEAD -> main, origin/main)`: Shows local `main` and `origin/main` point to same commit
- **This proves local and remote are in sync**

---

### Step 2.5: Verify on Remote Platform

**Instructions:**
1. Open your browser
2. Navigate to your repository URL (e.g., `https://github.com/johndoe/git-team-lab`)
3. Verify:
   - `README.md` is visible and displays correctly
   - `.gitignore` exists in file list
   - Commit message appears: "Initial commit: Add README and gitignore"
   - Branch dropdown shows `main` (not `master`)

**This is the final proof that push succeeded.**

---

## Part 3: Professional Sanity Checks (Prevent Future Push Problems)

Before starting any coding work, run this checklist. These checks prevent 90% of common push/pull failures.

### Checkpoint 1: Git Identity Configuration

**Commands:**
```bash
git config --global user.name
git config --global user.email
```

**What to look for:**
- `user.name`: Your full name (e.g., "Jane Doe")
- `user.email`: Your email (e.g., "jane.doe@example.com")

**What breaks if not set:**
- Commits will have incorrect author information
- Some Git servers reject commits without proper identity
- Team can't identify who made changes

**Fix if missing:**
```bash
git config --global user.name "Your Full Name"
git config --global user.email "your.email@example.com"
```

---

### Checkpoint 2: Remote Address Correctness

**Command:**
```bash
git remote -v
```

**What to look for:**
- `origin` points to correct repository URL
- Both fetch and push URLs are present
- URL matches your GitHub/GitLab/Bitbucket repository

**What breaks if incorrect:**
- Push goes to wrong repository (or fails with 403/404)
- Pull fetches wrong code

**Fix if incorrect:**
```bash
git remote set-url origin <CORRECT_URL>
```

---

### Checkpoint 3: Upstream Tracking Exists

**Command:**
```bash
git branch -vv
```

**What to look for:**
- Current branch shows `[origin/<branch-name>]` in brackets
- Example: `* main a1b2c3d [origin/main] Initial commit`

**What breaks if missing:**
- `git push` fails: "The current branch has no upstream branch"
- Must manually specify destination every time

**Fix if missing:**
```bash
git push -u origin <branch-name>
```

---

### Checkpoint 4: Working Tree is Clean

**Command:**
```bash
git status
```

**What to look for:**
- "nothing to commit, working tree clean"
- OR: Clear list of modified/staged files (if you're mid-work)

**What breaks if dirty:**
- Merge conflicts more likely
- Can't switch branches cleanly
- Unclear what will be committed

**Fix if dirty (choose one):**
```bash
git add .
git commit -m "Describe changes"
```
OR
```bash
git stash
```

---

### Checkpoint 5: Ahead/Behind Status

**Command:**
```bash
git status -sb
```

**What to look for:**
- `## main...origin/main`: Branches are in sync
- `## main...origin/main [ahead 1]`: You have 1 unpushed commit
- `## main...origin/main [behind 2]`: Remote has 2 commits you don't have
- `## main...origin/main [ahead 1, behind 2]`: Diverged (both have unique commits)

**What it means:**
- **Ahead:** You need to push
- **Behind:** You need to pull
- **Diverged:** You need to pull (possibly resolve conflicts), then push

**This is your early warning system for push failures.**

---

## Part 4: Team Branching Strategy & Execution

### The Strategy: main/dev/feature/*

**Branch Roles:**

| Branch | Purpose | Who Merges Into It | Stability |
|--------|---------|---------------------|-----------|
| `main` | Production-ready code | Release manager (from `dev`) | Highest |
| `dev` | Integration/testing | Developers (from `feature/*`) | Medium |
| `feature/*` | Individual tasks | Developer (commits directly) | Lowest |

**Rules (MUST FOLLOW):**
1. **Never commit directly to `main`** (merge from `dev` only)
2. **Always branch from `dev`** (not from `main` or other features)
3. **Always pull `dev` before creating a feature branch** (get latest code)
4. **Always inspect what will be merged before merging** (prevent surprises)
5. **Delete feature branches after merging** (keep repo clean)

---

### Step 4.1: Create `dev` Branch and Push It

**Commands:**
```bash
git checkout -b dev
```

**What it does:**
- `-b dev`: Creates a new branch named "dev"
- `checkout`: Switches to the new branch
- Copies current commit (from `main`) as starting point

**Why it's needed:**
- Establishes the integration branch
- Separates unstable work (`dev`) from stable code (`main`)

**Verification:**
```bash
git branch
```

**What to look for:**
- Output:
  ```
    main
  * dev
  ```
- `*` indicates you're on `dev`

---

**Command:**
```bash
git push -u origin dev
```

**What it does:**
- Pushes `dev` branch to remote
- `-u`: Sets upstream tracking (`dev` → `origin/dev`)

**Verification:**
```bash
git branch -vv
```

**What to look for:**
- Output:
  ```
    main a1b2c3d [origin/main] Initial commit
  * dev  a1b2c3d [origin/dev] Initial commit
  ```
- Both branches track their remote counterparts

```bash
git branch -r
```

**What to look for:**
- Output:
  ```
  origin/dev
  origin/main
  ```
- **This proves `dev` exists on remote**

---

### Step 4.2: Create a Feature Branch Correctly

**Commands:**
```bash
git checkout dev
```

**What it does:**
- Switches to `dev` branch
- Updates working directory to match `dev`'s latest commit

**Why it's needed:**
- Feature branches must start from `dev` (not `main` or another feature)
- Ensures you're building on the integration branch

---

**Command:**
```bash
git pull
```

**What it does:**
- Fetches latest commits from `origin/dev`
- Merges them into your local `dev`
- Ensures you have the team's latest work

**Why it's needed:**
- **Critical:** Someone else might have merged features while you were away
- Without this, your feature branch starts from outdated code
- Leads to merge conflicts later

**What breaks if you skip it:**
- Your feature is based on old code
- When merging back, you'll conflict with recent changes
- Wastes time resolving avoidable conflicts

**Expected output (if up to date):**
```
Already up to date.
```

**OR (if behind):**
```
Updating a1b2c3d..e4f5g6h
Fast-forward
 README.md | 2 ++
 1 file changed, 2 insertions(+)
```

---

**Command:**
```bash
git checkout -b feature/add-installation-guide
```

**What it does:**
- Creates and switches to `feature/add-installation-guide`
- Starts from current `dev` commit (because you're on `dev`)

**Naming convention:**
- `feature/`: Prefix for feature branches
- `add-installation-guide`: Descriptive name (kebab-case)
- Other prefixes: `bugfix/`, `hotfix/`, `refactor/`

**Verification:**
```bash
git branch
```

**What to look for:**
- Output:
  ```
    dev
  * feature/add-installation-guide
    main
  ```

```bash
git status
```

**What to look for:**
- `On branch feature/add-installation-guide`
- "nothing to commit, working tree clean"

---

### Step 4.3: Make a Change and Commit

**Command:**
````bash
cat >> README.md << 'EOF'


## Installation

1. Clone this repository:
   ```
   git clone <REMOTE_URL>
   cd git-team-lab
   ```

2. Install dependencies (if applicable):
   ```
   npm install
   ```

3. Start working on a feature branch:
   ```
   git checkout dev
   git pull
   git checkout -b feature/your-feature-name
   ```
EOF
````
--
**What it does:**
- Appends installation instructions to `README.md`
- `>>`: Append (don't overwrite)

**Verification:**
```bash
cat README.md
```

**What to look for:**
- New "Installation" section at the end

---

**Commands:**
```bash
git add README.md
git commit -m "Add installation guide to README"
```

**Verification:**
```bash
git log --oneline --decorate --graph --all -n 5
```

**What to look for:**
- Output:
  ```
  * b2c3d4e (HEAD -> feature/add-installation-guide) Add installation guide to README
  * a1b2c3d (origin/main, origin/dev, main, dev) Initial commit: Add README and gitignore
  ```
- `HEAD -> feature/add-installation-guide`: You're on the feature branch
- Feature branch is 1 commit ahead of `dev`

---

### Step 4.4: Push Feature Branch

**Command:**
```bash
git push -u origin feature/add-installation-guide
```

**What it does:**
- Pushes feature branch to remote
- Sets upstream tracking

**Why it's needed:**
- Backs up your work
- Allows team to see your progress
- Required for pull requests (GitHub/GitLab workflow)

**Verification:**
```bash
git branch -vv
```

**What to look for:**
- Output:
  ```
  * feature/add-installation-guide b2c3d4e [origin/feature/add-installation-guide] Add installation guide
  ```

```bash
git branch -r
```

**What to look for:**
- Output includes: `origin/feature/add-installation-guide`

---

### Step 4.5: Merge Feature → Dev Safely

**Step 4.5.1: Switch to `dev` and Pull Latest**

**Commands:**
```bash
git checkout dev
git pull
```

**What it does:**
- Switches to `dev`
- Fetches and merges latest changes from `origin/dev`

**Why it's needed:**
- **Critical:** Ensures you're merging into the latest `dev`
- Someone might have merged another feature while you worked
- Without this, you might overwrite their work

**Expected output:**
```
Already up to date.
```

---

**Step 4.5.2: Inspect What Will Be Merged**

**Command:**
```bash
git log --oneline --decorate --graph --all -n 20
```

**What to look for:**
- Visual graph showing branch divergence
- Example:
  ```
  * b2c3d4e (origin/feature/add-installation-guide, feature/add-installation-guide) Add installation guide
  * a1b2c3d (HEAD -> dev, origin/main, origin/dev, main) Initial commit
  ```
- Shows `feature/add-installation-guide` is 1 commit ahead of `dev`

---

**Command:**
```bash
git diff dev..feature/add-installation-guide
```

**What it does:**
- Shows exact line-by-line changes between `dev` and the feature branch
- `..`: Compares two branches

**What to look for:**
- Green lines (`+`): Additions
- Red lines (`-`): Deletions
- Should match your intended changes
- **If you see unexpected changes, STOP and investigate**

**Why this inspection is critical:**
- Prevents accidental merges of wrong code
- Catches mistakes before they enter `dev`
- Professional teams ALWAYS review before merging

---

**Step 4.5.3: Merge**

**Command:**
```bash
git merge feature/add-installation-guide
```

**What it does:**
- Merges feature branch into `dev`
- Creates a merge commit (or fast-forward if possible)
- Updates `dev` pointer to include feature commits

**Expected output (fast-forward):**
```
Updating a1b2c3d..b2c3d4e
Fast-forward
 README.md | 15 +++++++++++++++
 1 file changed, 15 insertions(+)
```

**Fast-forward:** No merge commit needed (linear history)

**OR (merge commit):**
```
Merge made by the 'recursive' strategy.
 README.md | 15 +++++++++++++++
 1 file changed, 15 insertions(+)
```

---

**Step 4.5.4: Verify Merge Success**

**Commands:**
```bash
git status
```

**What to look for:**
- "On branch dev"
- "Your branch is ahead of 'origin/dev' by 1 commit"
- "nothing to commit, working tree clean"

```bash
git log --oneline --decorate --graph --all -n 10
```

**What to look for:**
- `dev` and `feature/add-installation-guide` point to same commit
- Example:
  ```
  * b2c3d4e (HEAD -> dev, origin/feature/add-installation-guide, feature/add-installation-guide) Add installation guide
  * a1b2c3d (origin/main, origin/dev, main) Initial commit
  ```

---

**Step 4.5.5: Push `dev`**

**Command:**
```bash
git push
```

**What it does:**
- Pushes local `dev` to `origin/dev`
- No need for `-u` (tracking already set)

**Verification:**
```bash
git status -sb
```

**What to look for:**
- `## dev...origin/dev`
- No `[ahead]` or `[behind]` (in sync)

---

### Step 4.6: Merge Dev → Main Safely (Release Step)

**Step 4.6.1: Switch to `main` and Pull**

**Commands:**
```bash
git checkout main
git pull
```

**What it does:**
- Switches to `main`
- Ensures you have latest production code

---

**Step 4.6.2: Inspect Diff**

**Command:**
```bash
git diff main..dev
```

**What to look for:**
- All changes accumulated in `dev` since last release
- Should include your installation guide changes
- **Review carefully—this is going to production**

---

**Step 4.6.3: Merge**

**Command:**
```bash
git merge dev
```

**Expected output:**
```
Updating a1b2c3d..b2c3d4e
Fast-forward
 README.md | 15 +++++++++++++++
 1 file changed, 15 insertions(+)
```

---

**Step 4.6.4: Push `main`**

**Command:**
```bash
git push
```

**Verification:**
```bash
git log --oneline --decorate --graph --all -n 10
```

**What to look for:**
- Output:
  ```
  * b2c3d4e (HEAD -> main, origin/main, origin/dev, dev, origin/feature/add-installation-guide, feature/add-installation-guide) Add installation guide
  * a1b2c3d Initial commit
  ```
- `main`, `origin/main`, `dev`, and `origin/dev` all point to same commit
- **This proves release is complete**

---

### Step 4.7: Clean Up Feature Branch (Optional but Recommended)

**Commands:**
```bash
git branch -d feature/add-installation-guide
git push origin --delete feature/add-installation-guide
```

**What it does:**
- `-d`: Deletes local feature branch (safe delete—only works if merged)
- `--delete`: Deletes remote feature branch

**Why it's needed:**
- Keeps branch list clean
- Prevents confusion (feature is done)
- Professional teams delete merged branches

---

## Part 5: Debugging & "Never Have Push Surprises" Checklist

### When You Think You Pushed But Nothing Happened

Run these commands in order. Each reveals a piece of the puzzle.

#### Command 1: Where Am I?

```bash
git branch
```

**What it tells you:**
- Which branch you're currently on (`*` marker)
- All local branches

**Common mistake:**
- You think you're on `main`, but you're on `feature/xyz`
- Push succeeded, but to the wrong branch

---

#### Command 2: Where Does This Branch Push To?

```bash
git remote -v
```

**What it tells you:**
- Remote URL (is it correct?)
- Fetch vs push URLs

**Common mistake:**
- Remote URL is wrong (typo, wrong repo)
- Pushing to your fork instead of team repo

---

#### Command 3: Is Upstream Tracking Set?

```bash
git branch -vv
```

**What it tells you:**
- `[origin/branch-name]`: Tracking is set
- No brackets: **No tracking** (push will fail)

**Common mistake:**
- First push without `-u` flag
- Branch exists locally but not remotely

---

#### Command 4: Are There Uncommitted Changes?

```bash
git status
```

**What it tells you:**
- Modified files (red): Not staged
- Staged files (green): Ready to commit
- "nothing to commit": All changes committed

**Common mistake:**
- You edited files but didn't commit
- Push succeeded, but changes aren't in the commit

---

#### Command 5: What's the Commit History?

```bash
git log --oneline --decorate -n 10
```

**What it tells you:**
- Recent commits
- Where `HEAD`, local branches, and remote branches point

**Common mistake:**
- You committed to wrong branch
- Remote is ahead (you're behind)

---

#### Command 6: Am I Ahead or Behind?

```bash
git status -sb
```

**What it tells you:**
- `[ahead 2]`: You have 2 unpushed commits
- `[behind 3]`: Remote has 3 commits you don't have
- `[ahead 1, behind 2]`: Diverged

**Common mistake:**
- You're behind → push fails (non-fast-forward)
- Need to pull first

---

## Part 6: Common Failures & Professional Fixes

### Failure 1: "fatal: No configured push destination"

**Full error:**
```
fatal: The current branch feature/xyz has no upstream branch.
To push the current branch and set the remote as upstream, use

    git push --set-upstream origin feature/xyz
```

**Cause:**
- You created a branch locally but never pushed it
- No upstream tracking configured

**Diagnosis:**
```bash
git branch -vv
```

**What to look for:**
- Current branch has no `[origin/...]` in brackets

**Fix:**
```bash
git push -u origin <branch-name>
```

**Example:**
```bash
git push -u origin feature/xyz
```

**What it does:**
- Pushes branch to remote
- Sets upstream tracking for future pushes

**Verification:**
```bash
git branch -vv
```

**What to look for:**
- `[origin/feature/xyz]` now appears

---

### Failure 2: "rejected (non-fast-forward)"

**Full error:**
```
To https://github.com/user/repo.git
 ! [rejected]        main -> main (non-fast-forward)
error: failed to push some refs to 'https://github.com/user/repo.git'
hint: Updates were rejected because the tip of your current branch is behind
hint: its remote counterpart. Integrate the remote changes (e.g.
hint: 'git pull ...') before pushing again.
```

**Cause:**
- Remote has commits you don't have
- Your local branch is behind
- Git refuses to overwrite remote commits

**Diagnosis:**
```bash
git status -sb
```

**What to look for:**
- `[behind X]` or `[ahead Y, behind Z]`

**Fix (Option 1: Merge):**
```bash
git pull
git push
```

**What it does:**
- `git pull`: Fetches remote commits and merges them
- Creates a merge commit
- `git push`: Pushes the merged result

**Fix (Option 2: Rebase - Cleaner History):**
```bash
git pull --rebase
git push
```

**What it does:**
- `--rebase`: Fetches remote commits and replays your commits on top
- Avoids merge commit (linear history)
- **Preferred for feature branches**

**Rebase vs Merge (High-Level):**
- **Merge:** Preserves exact history (shows when branches diverged)
- **Rebase:** Rewrites history (makes it look like you started from latest)
- **Rule:** Use rebase for local branches, merge for shared branches

**Verification:**
```bash
git status -sb
```

**What to look for:**
- No `[behind]` indicator
- `[ahead X]` if you have new commits

---

### Failure 3: "I Don't See My Code on GitHub"

**Symptoms:**
- Push succeeded (no errors)
- Code not visible on GitHub/GitLab

**Diagnosis Steps:**

**Step 1: Which branch did you push?**
```bash
git branch
```

**What to look for:**
- `*` shows current branch
- Did you push a different branch than you intended?

---

**Step 2: Which remote branches exist?**
```bash
git branch -r
```

**What to look for:**
- List of `origin/*` branches
- Is your branch in the list?

**Example:**
```
origin/dev
origin/feature/xyz
origin/main
```

---

**Step 3: Where did the push go?**
```bash
git remote -v
```

**What to look for:**
- Is the URL correct?
- Did you push to a fork instead of the main repo?

---

**Step 4: Check GitHub/GitLab branch dropdown**
- Go to repository on web
- Click branch dropdown (usually shows "main" by default)
- Look for your branch name
- **If found:** Code is there, just not on `main`

---

**Common causes:**
1. **Pushed to feature branch, looking at `main`**
   - Fix: Switch branch on GitHub UI
2. **Pushed to wrong remote**
   - Fix: `git remote -v`, correct URL, push again
3. **Pushed to fork instead of upstream**
   - Fix: Add correct remote, push there

---

## Part 7: Final Practical Test / Submission

### Proof Pack: Terminal Outputs

Run these commands and save the output. This proves your repository is correctly configured.

#### Proof 1: Repository Structure

**Command:**
```bash
ls -a
```

**What to look for:**
- `.git` directory (proves Git is initialized)
- `README.md` (project documentation)
- `.gitignore` (ignore rules)

---

**Command:**
```bash
git status
```

**What to look for:**
- "On branch [branch-name]"
- "Your branch is up to date with 'origin/[branch-name]'"
- "nothing to commit, working tree clean"

**What it proves:**
- Repository is clean (no uncommitted changes)
- Branch is tracked and synced with remote

---

#### Proof 2: Remote Configuration

**Command:**
```bash
git remote -v
```

**What to look for:**
- `origin` with correct GitHub/GitLab URL
- Both fetch and push URLs present

**What it proves:**
- Remote is configured
- Push/pull destination is correct

---

#### Proof 3: Branch Tracking

**Command:**
```bash
git branch -vv
```

**What to look for:**
- Each branch shows `[origin/branch-name]` in brackets
- Example:
  ```
  * dev  b2c3d4e [origin/dev] Add installation guide
    main a1b2c3d [origin/main] Initial commit
  ```

**What it proves:**
- Upstream tracking is configured
- Simple `git push` will work

---

#### Proof 4: Remote Branches

**Command:**
```bash
git branch -r
```

**What to look for:**
- List of `origin/*` branches
- Should include at least: `origin/main`, `origin/dev`

**What it proves:**
- Branches exist on remote server
- Push succeeded

---

#### Proof 5: Commit History & Branch Graph

**Command:**
```bash
git log --oneline --decorate --graph --all -n 30
```

**What to look for:**
- Graph showing branch relationships
- Commits with proper messages
- Branch pointers (`HEAD`, `main`, `origin/main`, etc.)

**Example output:**
```
* b2c3d4e (HEAD -> main, origin/main, origin/dev, dev) Add installation guide
* a1b2c3d (origin/feature/add-installation-guide) Initial commit: Add README and gitignore
```

**What it proves:**
- Commit history is correct
- Branches are properly merged
- Local and remote are in sync

---

### Submission Checklist

Before submitting, verify:

- [ ] All commands in Proof Pack run without errors
- [ ] `git remote -v` shows correct repository URL
- [ ] `git branch -vv` shows upstream tracking for all branches
- [ ] `git status` shows "working tree clean"
- [ ] Repository is visible on GitHub/GitLab with all commits
- [ ] `main` and `dev` branches exist on remote
- [ ] At least one feature branch was created, merged, and deleted

**Optional:** Take screenshots of:
1. GitHub repository page showing branches
2. Terminal output of `git log --graph --all`
3. GitHub network graph (Insights → Network)

---

## Summary: Key Takeaways

### Mental Model
- **Local repo** (.git folder) is independent from **remote repo** (GitHub)
- **Upstream tracking** links local branches to remote branches
- **Always verify** before assuming success

### Critical Commands
- `git remote -v`: Check remote URL
- `git branch -vv`: Check upstream tracking
- `git status -sb`: Check ahead/behind status
- `git log --graph --all`: Visualize branch history

### Workflow Rules
1. Always pull before creating feature branches
2. Always inspect before merging (`git diff`, `git log`)
3. Never commit directly to `main`
4. Always verify push succeeded (`git branch -r`)

### Debugging Approach
1. Run diagnostic commands (don't guess)
2. Read error messages carefully
3. Check one thing at a time
4. Verify fix worked before continuing

---

## Next Steps

**Practice this workflow:**
1. Create 3 more feature branches
2. Make different changes in each
3. Merge them one by one into `dev`
4. Release `dev` to `main`
5. Practice resolving a merge conflict (create one intentionally)

**Advanced topics to explore:**
- Pull requests (GitHub/GitLab UI workflow)
- Rebasing vs merging strategies
- Git hooks (pre-commit, pre-push)
- Resolving merge conflicts
- Cherry-picking commits
- Interactive rebase (`git rebase -i`)

**Resources:**
- [Pro Git Book](https://git-scm.com/book/en/v2) (free, comprehensive)
- [GitHub Guides](https://guides.github.com/)
- [GitLab Documentation](https://docs.gitlab.com/)

---

**End of Lab**
