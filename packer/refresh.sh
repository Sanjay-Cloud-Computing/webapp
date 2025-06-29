#!/bin/bash

set -e

LAUNCH_TEMPLATE_NAME=$(aws ec2 describe-launch-templates --query "LaunchTemplates | sort_by(@, &CreateTime)[-1].LaunchTemplateName" --output text)
if [[ -z "$LAUNCH_TEMPLATE_NAME" ]]; then
    echo "ERROR: No Launch Template found."
    exit 1
fi

echo "Fetching the latest Auto Scaling Group..."
AUTO_SCALING_GROUP_NAME=$(aws autoscaling describe-auto-scaling-groups --query "AutoScalingGroups | sort_by(@, &CreatedTime)[-1].AutoScalingGroupName" --output text)
if [[ -z "$AUTO_SCALING_GROUP_NAME" ]]; then
    echo "ERROR: No Auto Scaling Group found."
    exit 1
fi

echo "Latest Auto Scaling Group: $LATEST_ASG_NAME"


echo "Fetching the latest AMI ID..."
NEW_AMI_ID=$(aws ec2 describe-images --filters "Name=state,Values=available" --query "Images | sort_by(@, &CreationDate)[-1].ImageId" --output text)
if [[ -z "$NEW_AMI_ID" ]]; then
    echo "ERROR: Failed to fetch the latest AMI ID."
    exit 1
fi
echo "Latest AMI ID: $NEW_AMI_ID"

echo "Creating a new Launch Template version..."
EXISTING_TEMPLATE_VERSION=$(aws ec2 describe-launch-templates --launch-template-names "$LAUNCH_TEMPLATE_NAME" --query "LaunchTemplates[0].LatestVersionNumber" --output text 2>/dev/null)
if [[ -z "$EXISTING_TEMPLATE_VERSION" ]]; then
    echo "ERROR: Failed to retrieve the latest version number for launch template: $LAUNCH_TEMPLATE_NAME"
    exit 1
else
    echo "Latest Version Number of Launch Template '$LAUNCH_TEMPLATE_NAME': $EXISTING_TEMPLATE_VERSION"
fi


NEW_TEMPLATE_VERSION=$(aws ec2 create-launch-template-version --launch-template-name "$LAUNCH_TEMPLATE_NAME" --source-version "$EXISTING_TEMPLATE_VERSION" --launch-template-data "{\"ImageId\": \"$NEW_AMI_ID\"}" --query "LaunchTemplateVersion.VersionNumber" --output text)
if [[ -z "$NEW_TEMPLATE_VERSION" ]]; then
    echo "ERROR: Failed to create a new Launch Template version."
    exit 1
fi
echo "New Launch Template Version: $NEW_TEMPLATE_VERSION"


echo "Updating Auto Scaling Group with the new Launch Template..."
aws autoscaling update-auto-scaling-group \
    --auto-scaling-group-name "$AUTO_SCALING_GROUP_NAME" \
    --launch-template "{\"LaunchTemplateName\": \"$LAUNCH_TEMPLATE_NAME\", \"Version\": \"$NEW_TEMPLATE_VERSION\"}"

echo "Auto Scaling Group updated successfully."


echo "Starting Instance Refresh..."
REFRESH_ID=$(aws autoscaling start-instance-refresh --auto-scaling-group-name "$AUTO_SCALING_GROUP_NAME" --query "InstanceRefreshId" --output text)
if [[ -z "$REFRESH_ID" ]]; then
    echo "ERROR: Failed to start the Instance Refresh."
    exit 1
fi
echo "Instance Refresh ID: $REFRESH_ID"

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
