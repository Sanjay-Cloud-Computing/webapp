#!/bin/bash

set -e

# Variables (Replace placeholders with your actual values)
LAUNCH_TEMPLATE_NAME="csye6225_asg"
# Get the latest Auto Scaling Group
echo "Fetching the latest Auto Scaling Group..."
LATEST_ASG_NAME=$(aws autoscaling describe-auto-scaling-groups --query "AutoScalingGroups | sort_by(@, &CreatedTime)[-1].AutoScalingGroupName" --output text)
if [[ -z "$LATEST_ASG_NAME" ]]; then
    echo "ERROR: Failed to fetch the latest Auto Scaling Group."
    exit 1
fi
echo "Latest Auto Scaling Group: $LATEST_ASG_NAME"


# Get the latest AMI ID
echo "Fetching the latest AMI ID..."
NEW_AMI_ID=$(aws ec2 describe-images --filters "Name=state,Values=available" --query "Images | sort_by(@, &CreationDate)[-1].ImageId" --output text)
if [[ -z "$NEW_AMI_ID" ]]; then
    echo "ERROR: Failed to fetch the latest AMI ID."
    exit 1
fi
echo "Latest AMI ID: $NEW_AMI_ID"

# Create a new launch template version with the latest AMI
echo "Creating a new Launch Template version..."
EXISTING_TEMPLATE_VERSION=$(aws ec2 describe-launch-templates --launch-template-names "$LAUNCH_TEMPLATE_NAME" --query "LaunchTemplates[0].LatestVersionNumber" --output text)
NEW_TEMPLATE_VERSION=$(aws ec2 create-launch-template-version --launch-template-name "$LAUNCH_TEMPLATE_NAME" --source-version "$EXISTING_TEMPLATE_VERSION" --launch-template-data "{\"ImageId\": \"$NEW_AMI_ID\"}" --query "LaunchTemplateVersion.VersionNumber" --output text)
if [[ -z "$NEW_TEMPLATE_VERSION" ]]; then
    echo "ERROR: Failed to create a new Launch Template version."
    exit 1
fi
echo "New Launch Template Version: $NEW_TEMPLATE_VERSION"

# Update the Auto Scaling Group with the new Launch Template version
echo "Updating Auto Scaling Group with the new Launch Template..."
aws autoscaling update-auto-scaling-group --auto-scaling-group-name "$AUTO_SCALING_GROUP_NAME" --launch-template "{\"LaunchTemplateName\": \"$LAUNCH_TEMPLATE_NAME\", \"Version\": \"$NEW_TEMPLATE_VERSION\"}"
echo "Auto Scaling Group updated successfully."

# Start an instance refresh
echo "Starting Instance Refresh..."
REFRESH_ID=$(aws autoscaling start-instance-refresh --auto-scaling-group-name "$AUTO_SCALING_GROUP_NAME" --query "InstanceRefreshId" --output text)
if [[ -z "$REFRESH_ID" ]]; then
    echo "ERROR: Failed to start the Instance Refresh."
    exit 1
fi
echo "Instance Refresh ID: $REFRESH_ID"

# Wait for the Instance Refresh to complete
echo "Waiting for Instance Refresh to complete..."
while true; do
    REFRESH_STATUS=$(aws autoscaling describe-instance-refreshes --auto-scaling-group-name "$AUTO_SCALING_GROUP_NAME" --query "InstanceRefreshes[?InstanceRefreshId=='$REFRESH_ID'].Status" --output text)
    echo "Current Instance Refresh Status: $REFRESH_STATUS"
    
    if [[ "$REFRESH_STATUS" == "Successful" ]]; then
        echo "Instance refresh completed successfully."
        break
    elif [[ "$REFRESH_STATUS" == "Failed" ]]; then
        echo "Instance refresh failed."
        exit 1
    else
        echo "Instance refresh in progress. Waiting..."
        sleep 30
    fi
done

echo "Script execution completed successfully."
