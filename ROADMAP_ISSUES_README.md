# Roadmap Issues Generator

This repository includes an automated GitHub Action that parses the `DEVELOPMENT_ROADMAP.md` file and creates GitHub issues for actionable tasks.

## How It Works

1. **Parser Script** (`roadmap_parser.py`): Parses the roadmap markdown file and extracts incomplete tasks with their details
2. **GitHub Action** (`.github/workflows/generate-roadmap-issues.yml`): Runs the parser and creates GitHub issues automatically

## Features

- 🔍 **Smart Parsing**: Extracts task titles, descriptions, priorities, and phases from the roadmap
- 🏷️ **Auto-Labeling**: Automatically applies relevant labels based on priority and phase
- 🚫 **Duplicate Prevention**: Skips creating issues that already exist
- ⚙️ **Configurable**: Control how many issues to create and filter by priority
- 📅 **Scheduled**: Runs automatically weekly, or manually on-demand

## Usage

### Manual Trigger

Go to the Actions tab in GitHub and run the "Generate Issues from Roadmap" workflow manually with these options:

- **Max Issues**: Maximum number of issues to create (default: 5)
- **Priority Filter**: Filter by priority level
  - `all`: Create issues for all priorities
  - `high`: Only high priority tasks
  - `medium`: Only medium priority tasks  
  - `low`: Only low priority tasks

### Automatic Schedule

The action runs automatically every Monday at 9 AM UTC to check for new roadmap tasks.

## Generated Issue Format

Each generated issue includes:

- **Title**: The main task title from the roadmap
- **Description**: Detailed sub-tasks and requirements
- **Labels**:
  - `priority:high|medium|low` - Based on roadmap priority
  - `phase:stability-&-performance|feature-enhancement|etc` - Based on roadmap phase
  - `type:enhancement` - Indicates this is an enhancement request
  - `roadmap-generated` - Identifies auto-generated issues

## Roadmap Format Requirements

The parser expects the roadmap to follow this structure:

```markdown
### Phase X: Phase Name (Timeline) 🔥 **HIGH PRIORITY**

#### X.X Section Name
- [ ] **Task Title**
  - Detailed requirement 1
  - Detailed requirement 2
  - Detailed requirement 3
- [x] **Completed Task** (will be ignored)
  - Already done items
```

### Priority Levels

- `HIGH PRIORITY` → `priority:high`
- `MEDIUM PRIORITY` → `priority:medium`
- `FUTURE ROADMAP` → `priority:low`
- No priority specified → `priority:low`

## Testing

Run the test suite to verify the parser works correctly:

```bash
python -m unittest test_roadmap_parser.py -v
```

## Customization

### Modify Issue Template

Edit the `to_issue_format()` method in `roadmap_parser.py` to customize:
- Issue body template
- Label naming conventions
- Priority mappings

### Adjust Workflow Settings

Edit `.github/workflows/generate-roadmap-issues.yml` to:
- Change the schedule frequency
- Modify default parameters
- Add additional issue processing logic

### Add New Priorities

Update both the parser and workflow to handle new priority levels by modifying:
1. Priority extraction logic in `parse()` method
2. Label mapping in `to_issue_format()` method
3. Workflow input options

## Permissions

The workflow requires these GitHub permissions:
- `issues: write` - To create issues
- `contents: read` - To read the roadmap file

## Troubleshooting

### No Issues Created

1. Check that there are incomplete tasks (`- [ ]`) in the roadmap
2. Verify the roadmap follows the expected format
3. Check workflow logs for parsing errors

### Duplicate Issues

The workflow automatically skips creating issues with titles that already exist. If you need to recreate an issue:
1. Close or rename the existing issue
2. Re-run the workflow

### Parser Errors

Run the parser locally to debug issues:

```bash
python roadmap_parser.py DEVELOPMENT_ROADMAP.md
```

This will output JSON data that can help identify parsing problems.

## Contributing

When updating the roadmap format or parser logic:

1. Run the test suite to ensure compatibility
2. Update this documentation if the format changes
3. Test the workflow manually before merging changes

---

*This system helps maintain alignment between the development roadmap and actionable GitHub issues, ensuring important tasks don't get forgotten.*