# sync-security-groups

This tool can be used to automatically update one or more AWS security groups to match a list of IP addresses.

Security group rules that specify other security groups instead of IP ranges will not be affected.

To find the desired list of IP addresses, the tool will perform an HTTP GET request to the URL that is specified in the
environment variable `IP_LIST_SOURCE`.

If the environment variable `IP_LIST_FORMAT` is `plain`, the document at the source URL should be simple text, one IP
address per line, like this:

    1.2.3.4
    5.6.7.8
    9.10.11.12

For each IP address in this list, the tool will create a security group rule granting ingress for all protocols on all
ports from the IP address (the /32 subnet). Any existing IP address rules in the security group that do not match this
list will be removed from the security group.

If the environment variable `IP_LIST_FORMAT` is `aws`, then set `IP_LIST_SOURCE` to
`https://ip-ranges.amazonaws.com/ip-ranges.json` (or a similar document) and the tool will extract all IPv4 address
ranges for the `ROUTE53_HEALTHCHECKS` service.

To specify which AWS security groups to update, use the environment variable `SECURITY_GROUP_IDS`. The format of this
variable is:

    <region>:<security_group_id> <region>:<security_group_id> ...

For example:

    SECURITY_GROUP_IDS="us-east-1:sg-10ed06353b8a49ecb us-west-2:sg-e601496e134643978"

You can specify as many security groups as you want. You must specify the region for each security group, and separate
each one with a space.

By default, calls to AWS will use `DryRun=True` and no changes will be made to your security groups. To actually update
your security groups, set the environment variable `DRY_RUN="False"`.

Provide your AWS credentials with the environment variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.

When the tool starts, it will immediately perform a sync. It will then sleep for a certain number of hours before
performing a sync again. The number of hours of sleep between syncs can be specified with the environment variable
`SYNC_INTERVAL`. The default behavior is `SYNC_INTERVAL=6`, or to perform a sync every 6 hours.

To disable the immediate sync when the tool is first started, set the environment variable `SYNC_ON_START=False`.

All log messages are emitted on standard output (stdout). You can control the log format and level with the environment
variables `LOG_FORMAT` and `LOG_LEVEL`. Defaults for these variables are:

    LOG_FORMAT="%(levelname)s [%(name)s] %(message)s"
    LOG_LEVEL="INFO"

To see all available placeholders for `LOG_FORMAT`, refer to [LogRecord attributes][a]. `LOG_LEVEL` can be any of
Python's default [logging levels][b].

[a]: https://docs.python.org/3/library/logging.html#logrecord-attributes
[b]: https://docs.python.org/3/library/logging.html#levels
