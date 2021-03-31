# github-fairy
Utility for teams with many repositories where automated pull requests are common. <br>

`github-fairy` uses Githubs graphql api together with api for reviewing and merging in a way to be able to efficiently handle  many PRs from for example `dependabot`. 

- Finds open PRs for repositories that your team has write access to
- Option to auto-approve a list of PRs by a specific user (like dependabot or other bot)

Created to learn some Python and do some good at the same time!

## Configuration
A personal github token needs to be created with the following scopes:

<ul>
  <li>repo</li>
  <li>read:org</li>
  <li>admin:repo_hook</li>
  <li>read:user</li>
</ul>

## Usage examples
```commandline
First time usage for configuration
> ./open-prs.py -t my-team -o mu-organization -T <my-token-here>

Auto approve all dependabot-PR:s (list of PRs shown before confirmation)

> ./open-prs.sh -a dependabot
```
## Acknowledgements
The solution was inspired by https://github.com/DeviesDevelopment/github-pr-tool/ <br>
This script provides a CLI interface that builds the automatic approval on top of it.