# open-prs
Utility to find open PRs in Github for a team.
Created to learn some Python and do some good at the same time!

##Configuration
Still at a very rudamental stage, so you will need to update `open-prs.sh` with your organization & team name. <br>
A personal github token needs to be created with the following scopes:

<ul>
  <li>repo</li>
  <li>read:org</li>
  <li>read:public_key</li>
  <li>read:repo_hook</li>
  <li>user</li>
  <li>read:gpg_key</li>
</ul>

The current implementation uses `secret-tool` in order to provide the token.
You can add your token to `secret-tool` using 
```
> secret-tool store fehlhabers open-prs
```
Otherwise, just pipe the token into the python-script.

##Usage
```commandline
> ./open-prs.sh <sort by>

EXAMPLE:
> ./open-prs.sh date
```
##Acknowledgements
The solution was originally done by https://github.com/DeviesDevelopment/github-pr-tool/ <br>
This script provides a CLI interface with similar capabilities.