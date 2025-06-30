# Repository Labels Setup

The labeller workflow requires specific labels to exist in the repository. Due to permission limitations, labels need to be created manually.

## 🚨 Current Issue

The GitHub Actions labeller is failing with:
```
Error: You do not have permission to create labels on this repository
```

This happens because the `GITHUB_TOKEN` doesn't have sufficient permissions to create labels, even with `issues: write` permission.

## ✅ Solution: Manual Label Creation

### Default Labels (Already Available)
These labels should already exist in most GitHub repositories:
- `bug` - Something isn't working
- `documentation` - Improvements or additions to documentation
- `enhancement` - New feature or request
- `dependencies` - Pull requests that update a dependency file

### Additional Recommended Labels
Create these labels manually via GitHub UI:

**Navigation:** Repository → Issues → Labels → New label

| Label Name | Color | Description |
|------------|-------|-------------|
| `core` | `#d73a4a` | Core application code changes |
| `testing` | `#7057ff` | Testing related changes |
| `docker` | `#1d76db` | Docker and deployment related |
| `ci` | `#2cbe4e` | Continuous integration and workflows |
| `config` | `#fbca04` | Configuration file changes |
| `refactor` | `#fef2c0` | Code refactoring |
| `chore` | `#ededed` | Maintenance and chores |
| `breaking` | `#b60205` | Breaking changes |
| `mcp` | `#0e8a16` | MCP (Model Context Protocol) specific |
| `security` | `#ee0701` | Security related changes |

## 🛠️ Manual Setup Steps

### 1. Access Labels Section
1. Go to your repository on GitHub
2. Click **Issues** tab
3. Click **Labels** (next to Milestones)

### 2. Create Missing Labels
For each label in the table above:
1. Click **New label**
2. Enter the **Label name**
3. Enter the **Color** (without #)
4. Enter the **Description**
5. Click **Create label**

### 3. Verify Labeller Configuration
After creating labels, the labeller workflow will automatically apply them based on:

- **File changes**: Documentation, core code, dependencies, etc.
- **Branch names**: feature/, fix/, refactor/, etc.

## 🔄 Alternative: Simplified Configuration

The current labeller configuration has been simplified to use only default GitHub labels:

```yaml
# Only uses existing labels to avoid permission issues
documentation:  # Default GitHub label
enhancement:    # Default GitHub label
bug:           # Default GitHub label
dependencies:  # Default GitHub label
```

This ensures the labeller works without requiring additional label creation.

## 🧪 Testing the Labeller

After setting up labels:

1. **Create a test PR** with documentation changes (modify a .md file)
2. **Check if labels are applied** automatically
3. **Verify branch-based labeling** by creating PR from feature/ branch

## 🔧 Troubleshooting

### Labels Not Applied
- Verify labels exist in repository
- Check labeller configuration syntax
- Review GitHub Actions logs for errors

### Permission Errors
- Ensure workflow has `pull-requests: write` permission
- Verify the workflow is using correct token parameter

### Configuration Issues
- Validate `.github/labeler.yml` syntax
- Check file path patterns match your repository structure
- Test with simple patterns first

## 📋 Future Improvements

### Repository Admin Options
If you have admin access to the repository:

1. **Create Personal Access Token** with `repo` scope
2. **Add as repository secret** (e.g., `LABELER_TOKEN`)
3. **Update workflow** to use custom token:
   ```yaml
   with:
     token: "${{ secrets.LABELER_TOKEN }}"
   ```

### Organization Settings
For organization repositories, admins can:
- Enable automatic label creation permissions
- Set up organization-wide label templates
- Configure default repository labels

---

**Repository Labels** - Automatic PR categorization for better project management 🏷️
