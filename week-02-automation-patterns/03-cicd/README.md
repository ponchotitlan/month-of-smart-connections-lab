# CI/CD for Ansible Network Automation

This folder contains documentation and resources for the CI/CD pipeline that automates network interface management using Ansible.

## GitHub Actions Workflow

The CI/CD pipeline is defined in `.github/workflows/ansible-ci.yml` at the repository root. While the workflow file must be in `.github/workflows/` to be recognized by GitHub, it operates on the Ansible project in the `week-02-automation-patterns/02-ansible/` directory.

### Why the workflow file is in `.github/workflows/`

GitHub Actions requires all workflow files to be located in the `.github/workflows/` directory at the repository root. This is a GitHub requirement and cannot be changed. However, the workflow:

- References and executes playbooks from `week-02-automation-patterns/02-ansible/`
- Uses the Ansible configuration and inventory from that directory
- Stores outputs and artifacts from the Ansible runs

## Manual Trigger

The workflow uses `workflow_dispatch` which allows you to trigger it manually from the GitHub UI.

### How to Trigger the Workflow

1. Go to your GitHub repository
2. Click on the **Actions** tab
3. Select **Ansible Network Automation CI** from the left sidebar
4. Click **Run workflow** button (on the right side)
5. Choose your options:
   - **Action to perform**: 
     - `get_interfaces` - Read current interface configurations
     - `configure_interfaces` - Apply interface configurations
     - `both` - Run both playbooks sequentially
   - **Target host**: (Optional) Specify a specific host to target, or leave empty for all hosts
6. Click the green **Run workflow** button

## Workflow Features

### Actions Available

- **Get Interfaces**: Retrieves current interface configurations from network devices
- **Configure Interfaces**: Applies interface configurations to network devices
- **Both**: Runs both operations in sequence (useful for verify-then-apply scenarios)

### Artifacts

The workflow automatically saves:

- **Ansible outputs**: JSON files and other outputs from the playbook runs (retained for 30 days)
- **Ansible logs**: Log files from the execution (retained for 7 days)

You can download these artifacts from the workflow run page.

### Environment Setup

The workflow automatically:

1. Sets up Python 3.11
2. Caches pip dependencies for faster runs
3. Installs all requirements from `requirements.txt`
4. Configures the working directory to the Ansible project folder

## Required GitHub Secrets

If your Ansible playbooks require authentication credentials, you'll need to configure GitHub Secrets:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add the following secrets as needed:
   - `ANSIBLE_USER`: Username for device access
   - `ANSIBLE_PASSWORD`: Password for device access
   - Any other credentials required by your inventory/playbooks

### Using Secrets in the Workflow

To use secrets in the workflow, modify the playbook execution steps in `.github/workflows/ansible-ci.yml`:

```yaml
env:
  ANSIBLE_HOST_KEY_CHECKING: 'False'
  ANSIBLE_USER: ${{ secrets.ANSIBLE_USER }}
  ANSIBLE_PASSWORD: ${{ secrets.ANSIBLE_PASSWORD }}
```

Or pass them as extra vars:

```yaml
run: |
  ansible-playbook get_interfaces.yml \
    -e "ansible_user=${{ secrets.ANSIBLE_USER }}" \
    -e "ansible_password=${{ secrets.ANSIBLE_PASSWORD }}"
```

## Local Testing

Before pushing changes, you can test the playbooks locally:

```bash
# Activate your virtual environment
source .venv/bin/activate

# Navigate to the Ansible directory
cd week-02-automation-patterns/02-ansible

# Run playbooks
ansible-playbook get_interfaces.yml
ansible-playbook configure_interfaces.yml

# Test with specific host
ansible-playbook get_interfaces.yml --limit devnet-sandbox-router-1
```

## Workflow Customization

### Adding More Actions

To add more playbook options, edit the workflow file and add to the `action` input choices:

```yaml
options:
  - get_interfaces
  - configure_interfaces
  - both
  - your_new_action  # Add here
```

Then add a corresponding step:

```yaml
- name: Run - Your New Action
  if: ${{ github.event.inputs.action == 'your_new_action' }}
  working-directory: week-02-automation-patterns/02-ansible
  run: |
    ansible-playbook your_playbook.yml
```

### Scheduled Runs

To add scheduled execution (in addition to manual triggers), add to the `on:` section:

```yaml
on:
  workflow_dispatch:
    # ... existing inputs ...
  schedule:
    - cron: '0 2 * * *'  # Run daily at 2 AM UTC
```

### Pull Request Validation

To run the workflow on pull requests (e.g., for validation):

```yaml
on:
  workflow_dispatch:
    # ... existing inputs ...
  pull_request:
    paths:
      - 'week-02-automation-patterns/02-ansible/**'
```

## Troubleshooting

### Workflow doesn't appear in Actions tab

- Ensure the workflow file is committed to the default branch (main/master)
- Check that the file is in `.github/workflows/` with a `.yml` or `.yaml` extension
- Verify the YAML syntax is valid

### Authentication failures

- Verify GitHub Secrets are configured correctly
- Check that secret names match exactly (case-sensitive)
- Ensure credentials are being passed to the playbook properly

### Connection timeouts

- Check if GitHub Actions runners can reach your network devices
- You may need to use self-hosted runners if devices are on a private network
- Consider using a VPN or bastion host in your workflow

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Ansible Documentation](https://docs.ansible.com/)
- [workflow_dispatch Event](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#workflow_dispatch)
