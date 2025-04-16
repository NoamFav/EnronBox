#!/bin/bash

# Script to sync issues between GitLab and GitHub, updating assignees
# Supports updating either platform or both

# Usage:
# ./issue-sync.sh --file issues-json.json [--gitlab] [--github]
# If neither --gitlab nor --github is specified, both will be updated

# Default configurations
GITLAB_URL="https://gitlab.maastrichtuniversity.nl"
GITLAB_PROJECT_ID="project2-2-2425/team03"
GITHUB_REPO="NoamFav/NLP_project"
GITHUB_API="https://api.github.com"
JSON_FILE=""

# Flag variables
DO_GITLAB=false
DO_GITHUB=false

# Process command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
    --file)
        JSON_FILE="$2"
        shift 2
        ;;
    --gitlab)
        DO_GITLAB=true
        shift
        ;;
    --github)
        DO_GITHUB=true
        shift
        ;;
    *)
        echo "Unknown option: $1"
        echo "Usage: ./issue-sync.sh --file issues-json.json [--gitlab] [--github]"
        exit 1
        ;;
    esac
done

# If neither is specified, do both
if [ "$DO_GITLAB" = false ] && [ "$DO_GITHUB" = false ]; then
    DO_GITLAB=false
    DO_GITHUB=false
fi

# Check if file is provided
if [ -z "$JSON_FILE" ]; then
    echo "Error: No JSON file specified. Use --file option."
    echo "Usage: ./issue-sync.sh --file issues-json.json [--gitlab] [--github]"
    exit 1
fi

# Check if the JSON file exists
if [ ! -f "$JSON_FILE" ]; then
    echo "Error: JSON file '$JSON_FILE' not found"
    exit 1
fi

# Get tokens from environment or .zshrc
get_tokens() {
    # Try to get tokens from environment
    GITLAB_TOKEN=${GITLAB_TOKEN:-""}
    GITHUB_TOKEN=${BOT_GITHUB_TOKEN:-""}

    # If not found, try to get from .zshrc
    if [ -f ~/.zshrc ]; then
        if [ -z "$GITLAB_TOKEN" ]; then
            GITLAB_TOKEN=$(grep -o 'GITLAB_TOKEN=[^"]*' ~/.zshrc | cut -d= -f2)
        fi
        if [ -z "$GITHUB_TOKEN" ]; then
            GITHUB_TOKEN=$(grep -o 'GITHUB_TOKEN=[^"]*' ~/.zshrc | cut -d= -f2)
        fi
    fi

    # Validate we have the tokens we need
    if [ "$DO_GITLAB" = true ] && [ -z "$GITLAB_TOKEN" ]; then
        echo "Error: GitLab token not found. Please set GITLAB_TOKEN environment variable."
        exit 1
    fi

    if [ "$DO_GITHUB" = true ] && [ -z "$GITHUB_TOKEN" ]; then
        echo "Error: GitHub token not found. Please set GITHUB_TOKEN environment variable."
        exit 1
    fi
}

# Check if jq is installed
check_dependencies() {
    if ! command -v jq &>/dev/null; then
        echo "Error: jq is required but not installed. Please install jq."
        echo "You can install it using:"
        echo "  - On macOS: brew install jq"
        echo "  - On Ubuntu/Debian: sudo apt-get install jq"
        echo "  - On CentOS/RHEL: sudo yum install jq"
        exit 1
    fi
}

# Function to get GitLab user ID from name
get_gitlab_user_id() {
    local name="$1"

    if [ "$name" = "NoamFavier" ]; then
        echo "1163" # Noam Favier
    elif [ "$name" = "RemiDubois" ]; then
        echo "1227" # Remi
    elif [ "$name" = "JiangWei" ]; then
        echo "1246" # Jiang
    elif [ "$name" = "EstebanMarquez" ]; then
        echo "1248" # Esteban
    elif [ "$name" = "OctavianIonescu" ]; then
        echo "1332" # Octavian
    elif [ "$name" = "GiorgosPapadopoulos" ]; then
        echo "1349" # Giorgos
    else
        echo ""
    fi
}

# Function to get GitHub username from original name
get_github_username() {
    local name="$1"

    if [ "$name" = "NoamFavier" ]; then
        echo "NoamFav"
    elif [ "$name" = "RemiDubois" ]; then
        echo "RemiHeijmans"
    elif [ "$name" = "JiangWei" ]; then
        echo "DuckBloodJ"
    elif [ "$name" = "EstebanMarquez" ]; then
        echo "estebann23"
    elif [ "$name" = "OctavianIonescu" ]; then
        echo "OctavianUM"
    elif [ "$name" = "GiorgosPapadopoulos" ]; then
        echo "GiorgosdeJonge"
    else
        echo ""
    fi
}

# Find GitLab issue ID by title
get_gitlab_issue_id() {
    local title="$1"
    local escaped_title=$(echo "$title" | sed 's/"/\\"/g')

    local response=$(curl -s -G \
        --data-urlencode "search=$escaped_title" \
        -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
        "${GITLAB_URL}/api/v4/projects/$(echo ${GITLAB_PROJECT_ID} | sed 's/\//%2F/g')/issues")

    # Try to find the exact issue by title
    local issue_id=$(echo "$response" | jq -r ".[] | select(.title == \"$escaped_title\") | .iid")

    echo "$issue_id"
}

# Find GitHub issue number by title
get_github_issue_number() {
    local title="$1"
    local escaped_title=$(echo "$title" | sed 's/"/\\"/g')

    # GitHub search API is not as precise, so we'll get all issues and filter
    local response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "${GITHUB_API}/repos/${GITHUB_REPO}/issues?state=all&per_page=100")

    # Find the issue with matching title
    local issue_number=$(echo "$response" | jq -r ".[] | select(.title == \"$escaped_title\") | .number")

    echo "$issue_number"
}

# Update GitLab issue assignee
update_gitlab_assignee() {
    local issue_iid="$1"
    local user_id="$2"

    echo "GitLab: Updating issue #$issue_iid: Assigning to user ID $user_id"

    response=$(curl -s -X PUT \
        -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
      \"assignee_ids\": [$user_id]
    }" \
        "${GITLAB_URL}/api/v4/projects/$(echo ${GITLAB_PROJECT_ID} | sed 's/\//%2F/g')/issues/${issue_iid}")

    # Check if the request was successful
    if echo "$response" | jq -e '.id' >/dev/null; then
        echo "✅ GitLab: Successfully updated issue #$issue_iid"
    else
        echo "❌ GitLab: Failed to update issue #$issue_iid"
        echo "   Error: $(echo "$response" | jq -r '.message // "Unknown error"')"
    fi
}

# Update GitHub issue assignee
update_github_assignee() {
    local issue_number="$1"
    local username="$2"

    echo "GitHub: Updating issue #$issue_number: Assigning to user $username"

    response=$(curl -s -X PATCH \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        -H "Content-Type: application/json" \
        -d "{
      \"assignees\": [\"$username\"]
    }" \
        "${GITHUB_API}/repos/${GITHUB_REPO}/issues/${issue_number}")

    # Check if the request was successful
    if echo "$response" | jq -e '.id' >/dev/null; then
        echo "✅ GitHub: Successfully updated issue #$issue_number"
    else
        echo "❌ GitHub: Failed to update issue #$issue_number"
        echo "   Error: $(echo "$response" | jq -r '.message // "Unknown error"')"
    fi
}

# Create a new GitHub issue
create_github_issue() {
    local title="$1"
    local body="$2"
    local username="$3"
    local labels="$4"

    echo "GitHub: Creating new issue: $title"

    # Format labels for GitHub
    local github_labels="[]"
    if [ -n "$labels" ]; then
        github_labels=$(echo "$labels" | jq 'map({name: .})')
    fi

    # Create the issue
    response=$(curl -s -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        -H "Content-Type: application/json" \
        -d "{
      \"title\": \"$title\",
      \"body\": \"$body\",
      \"assignees\": [\"$username\"],
      \"labels\": $github_labels
    }" \
        "${GITHUB_API}/repos/${GITHUB_REPO}/issues")

    # Check if successful
    if echo "$response" | jq -e '.id' >/dev/null; then
        local issue_number=$(echo "$response" | jq -r '.number')
        echo "✅ GitHub: Successfully created issue #$issue_number"
    else
        echo "❌ GitHub: Failed to create issue: $title"
        echo "   Error: $(echo "$response" | jq -r '.message // "Unknown error"')"
    fi
}

# Process issues from JSON file
process_issues() {
    echo "Processing issues from JSON file: $JSON_FILE"
    local issue_count=$(jq '. | length' "$JSON_FILE")
    echo "Found $issue_count issues to process"

    jq -c '.[]' "$JSON_FILE" | while read -r issue; do
        local title=$(echo "$issue" | jq -r '.title')
        local body=$(echo "$issue" | jq -r '.body')
        local original_assignee=$(echo "$issue" | jq -r '.assignees[0]')
        local labels=$(echo "$issue" | jq '.labels')

        echo "Processing issue: $title"

        if [ -n "$original_assignee" ]; then
            # Handle GitLab update
            if [ "$DO_GITLAB" = true ]; then
                local gitlab_user_id=$(get_gitlab_user_id "$original_assignee")

                if [ -n "$gitlab_user_id" ]; then
                    local gitlab_issue_id=$(get_gitlab_issue_id "$title")

                    if [ -n "$gitlab_issue_id" ]; then
                        update_gitlab_assignee "$gitlab_issue_id" "$gitlab_user_id"
                    else
                        echo "⚠️ GitLab: Issue not found: $title"
                    fi
                else
                    echo "⚠️ GitLab: No user ID mapping for: $original_assignee"
                fi
            fi

            # Handle GitHub update or creation
            if [ "$DO_GITHUB" = true ]; then
                local github_username=$(get_github_username "$original_assignee")

                if [ -n "$github_username" ]; then
                    local github_issue_number=$(get_github_issue_number "$title")

                    if [ -n "$github_issue_number" ]; then
                        update_github_assignee "$github_issue_number" "$github_username"
                    else
                        echo "⚠️ GitHub: Issue not found, creating new issue: $title"
                        create_github_issue "$title" "$body" "$github_username" "$labels"
                    fi
                else
                    echo "⚠️ GitHub: No username mapping for: $original_assignee"
                fi
            fi
        else
            echo "⚠️ No assignee specified for issue: $title"
        fi

        # Add some spacing between issues for readability
        echo ""
    done
}

# Main execution
echo "Issue Synchronization Tool"
echo "--------------------------"
if [ "$DO_GITLAB" = true ]; then echo "✓ GitLab updates enabled"; fi
if [ "$DO_GITHUB" = true ]; then echo "✓ GitHub updates enabled"; fi
echo "Using JSON file: $JSON_FILE"
echo "--------------------------"

check_dependencies
get_tokens
process_issues

echo "All issues have been processed!"
