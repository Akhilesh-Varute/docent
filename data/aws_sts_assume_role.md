# AWS STS AssumeRole

## The problem it solves
One AWS account (the "caller") needs to do something inside a different AWS
account (the "target"), for example stop an EC2 instance. Sharing permanent
access keys between accounts is risky: they never expire, they get copied
around, and they are hard to revoke.

## How AssumeRole works
1. The target account creates an IAM role.
2. The role has a trust policy that says who is allowed to assume it, for
   example a specific account ID or a specific Lambda execution role.
3. The role has a permissions policy that says what it may do, for example
   ec2:DescribeInstances, ec2:StartInstances and ec2:StopInstances only.
4. The caller calls STS (the Security Token Service) with sts:AssumeRole and
   the role's ARN.
5. If the trust policy allows the caller, STS returns temporary credentials:
   an access key ID, a secret access key and a session token.
6. The caller builds a normal boto3 client using those credentials. Every
   call through that client acts inside the target account, with only the
   permissions of the role.
7. The credentials expire after a limited time (one hour by default), so
   nothing long-lived is stored.

## Why it is better than shared keys
- No permanent secrets to leak.
- Permissions are limited to what the role allows.
- The target account can revoke access at any time by editing the trust
  policy or deleting the role.
- Every assumed-role call is recorded in CloudTrail, so there is an audit
  trail.

## Multi-customer setups
When one service acts in many customers' accounts, a common extra safeguard
is an External ID: a value the customer puts in the role's trust policy and
the service must send when assuming the role. It prevents the "confused
deputy" problem, where one customer could trick the service into acting in
another customer's account.

## Common error
AccessDenied on AssumeRole usually means the trust policy does not list the
caller, or the caller itself lacks permission to call sts:AssumeRole.
