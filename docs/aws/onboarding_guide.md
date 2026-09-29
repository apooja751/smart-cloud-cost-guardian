# ☁️ AWS Account Connection & Onboarding Guide

Smart Cloud Cost Guardian connects to your AWS account using standard, secure AWS **Security Token Service (STS) Cross-Account IAM AssumeRole** with an `ExternalId`.

This architecture ensures:
1. **Zero Long-Lived Credentials**: No AWS Access Key ID or Secret Access Keys are ever stored.
2. **Advisory-Only / Read-Only**: SCCG cannot terminate instances, delete disks, or modify cloud infrastructure.
3. **Revocable Access**: You can revoke access immediately at any time by deleting the IAM Role in your AWS account.

---

## Method 1: Automated CloudFormation Setup (Recommended)

1. Sign in to your AWS Management Console.
2. Navigate to **CloudFormation** > **Create Stack** > **With new resources (standard)**.
3. Select **Upload a template file** and choose [`infrastructure/aws/cloudformation_role.yml`](../../infrastructure/aws/cloudformation_role.yml).
4. Enter the required stack parameters:
   - **Stack name**: `SCCG-FinOps-Role`
   - **SCCGAccountId**: The AWS Account ID of the SCCG deployment host.
   - **ExternalId**: The secure external ID shown in your SCCG account dashboard.
5. Check the box: *"I acknowledge that AWS CloudFormation might create IAM resources with custom names"*.
6. Click **Submit**.
7. Once the stack status reaches `CREATE_COMPLETE`, copy the **RoleArn** from the CloudFormation **Outputs** tab.
8. Paste the **RoleArn** and **ExternalId** into the SCCG **Connect AWS Account** modal.

---

## Method 2: Manual IAM Role Creation via AWS Console

### Step 1: Create IAM Policy
1. Navigate to **IAM** > **Policies** > **Create Policy**.
2. Click the **JSON** editor tab and paste the exact contents of [`infrastructure/aws/iam_policy.json`](../../infrastructure/aws/iam_policy.json).
3. Name the policy `SCCGReadOnlyFinOpsPolicy`.
4. Click **Create Policy**.

### Step 2: Create Cross-Account IAM Role
1. Navigate to **IAM** > **Roles** > **Create Role**.
2. Select **Custom trust policy** and paste:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "AWS": "arn:aws:iam::<SCCG_HOST_ACCOUNT_ID>:root"
         },
         "Action": "sts:AssumeRole",
         "Condition": {
           "StringEquals": {
             "sts:ExternalId": "<YOUR_EXTERNAL_ID>"
           }
         }
       }
     ]
   }
   ```
3. Attach the `SCCGReadOnlyFinOpsPolicy` created in Step 1.
4. Name the role `SCCGFinOpsAssessmentRole` and click **Create Role**.
5. Copy the newly created Role ARN (e.g., `arn:aws:iam::123456789012:role/SCCGFinOpsAssessmentRole`).

---

## Verification & Testing

Once connected in SCCG, navigate to **AWS Accounts** > click **Test Connection**:
- The backend calls `sts.assume_role()` with the provided Role ARN and External ID.
- Upon successful authentication, SCCG issues temporary credentials and pulls the initial resource inventory across EC2, EBS, RDS, S3, and CloudWatch metrics.
