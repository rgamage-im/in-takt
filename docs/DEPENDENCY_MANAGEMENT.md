# Dependency Management Guide

## Overview

This project uses **pip-tools** for dependency management and **Dependabot** for automated updates.

## Files

- **`requirements.in`** - Top-level dependencies (what you edit)
- **`requirements.txt`** - Fully pinned dependencies (auto-generated)
- **`requirements-dev.in`** - Development-only dependencies
- **`requirements-dev.txt`** - Pinned dev dependencies (auto-generated)

## Setup

### Install pip-tools

```bash
pip install pip-tools
```

## Workflow

### Adding a New Dependency

1. Add the package to `requirements.in` (or `requirements-dev.in` for dev tools)
   ```
   # requirements.in
   new-package>=1.0
   ```

2. Compile the requirements:
   ```bash
   pip-compile requirements.in
   pip-compile requirements-dev.in  # if you added dev deps
   ```

3. Install the new dependencies:
   ```bash
   pip-sync requirements.txt requirements-dev.txt
   ```

4. Test and commit both `.in` and `.txt` files

### Upgrading Dependencies

#### Upgrade a Single Package

```bash
pip-compile --upgrade-package package-name requirements.in
pip install -r requirements.txt
```

#### Upgrade All Packages

```bash
pip-compile --upgrade requirements.in
pip-compile --upgrade requirements-dev.in
pip-sync requirements.txt requirements-dev.txt
```

#### Upgrade Django (carefully!)

```bash
# Check Django release notes first
pip-compile --upgrade-package Django requirements.in
python manage.py migrate
pytest tests/
```

### Installing Dependencies

#### Production Environment

```bash
pip install -r requirements.txt
```

#### Development Environment

```bash
pip-sync requirements.txt requirements-dev.txt
# OR
pip install -r requirements.txt -r requirements-dev.txt
```

## Dependabot Integration

Dependabot automatically creates PRs for dependency updates weekly (Mondays at 9 AM PT).

### Configuration

- Weekly updates on Mondays
- Groups related packages (Azure, Django ecosystem, dev tools)
- Ignores Django major version updates (stay on LTS)
- Maximum 5 open PRs at a time

### Handling Dependabot PRs

1. **Review the PR** - Check changelog and breaking changes
2. **Test locally** if needed:
   ```bash
   gh pr checkout <PR-number>
   pip-sync requirements.txt requirements-dev.txt
   pytest tests/
   python manage.py check
   ```
3. **Merge** if tests pass
4. **Close** if update causes issues

### Customizing Dependabot

Edit `.github/dependabot.yml` to:
- Change update frequency
- Add/remove package groups
- Adjust ignore rules
- Modify reviewers/labels

## Best Practices

### ✅ DO

- Edit `requirements.in` files, never `requirements.txt` directly
- Run `pip-compile` after changing `.in` files
- Commit both `.in` and `.txt` files together
- Test after upgrading dependencies
- Use version constraints in `.in` files:
  - `package>=1.0,<2.0` - Allow minor updates
  - `Django>=5.2,<6.0` - Stay on LTS
  - `package==1.2.3` - Pin if needed

### ❌ DON'T

- Manually edit `requirements.txt`
- Run `pip freeze > requirements.txt`
- Skip testing after upgrades
- Mix production and dev dependencies

## Troubleshooting

### Dependency Conflicts

```bash
# See why a package is included
pip-compile --verbose requirements.in

# Check dependency tree
pip install pipdeptree
pipdeptree -p package-name
```

### Reset Everything

```bash
# Backup current state
cp requirements.txt requirements.txt.backup

# Clean recompile
pip-compile --rebuild requirements.in
pip-compile --rebuild requirements-dev.in
pip-sync requirements.txt requirements-dev.txt
```

### Rollback After Bad Update

```bash
git checkout HEAD~1 requirements.txt requirements-dev.txt
pip-sync requirements.txt requirements-dev.txt
```

## Migration from Old System

The upgrade scripts in `upgrade_scripts/` used `sed` to update `requirements.txt` directly. With pip-tools:

1. Update `requirements.in` instead
2. Run `pip-compile`
3. Test
4. Commit

Example:
```bash
# Old way
sed -i 's/^django==.*/django==5.2.8/' requirements.txt

# New way
# Edit requirements.in: Django>=5.2,<6.0
pip-compile requirements.in
```

## References

- [pip-tools documentation](https://pip-tools.readthedocs.io/)
- [Dependabot documentation](https://docs.github.com/en/code-security/dependabot)
- [Django LTS schedule](https://www.djangoproject.com/download/#supported-versions)
