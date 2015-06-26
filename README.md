# ec2list
Tool for list all running instances in aws accounts.

It require boto lib installed, as well as `~/.boto` file with credentials, or, environment variable pointed to `~/.aws/config`

```
export BOTO_CONFIG=~/.aws/config; ec2list
```
