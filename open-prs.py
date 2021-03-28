#!/usr/bin/python3

import requests
import sys
import os
import json
import keyring
from getpass import getpass
import argparse
from jproperties import Properties

PROPERTIES_FILE = 'config.properties'

ORGANIZATION = "organization"
TEAM = "team"
SERVICE_AND_USER = "open-prs"

CREATED_WIDTH = 10
REPO_WIDTH = 20
AUTHOR_WIDTH = 15
URL_WIDTH = 100
TITLE_WIDTH = 53


def get_query(end_cursor=""):
    graph_query = """{ "query" : "query {
      rateLimit {
        limit
        cost
        remaining
        resetAt
      }
      organization (login: \\"$ORGANIZATION\\") {
        name
        team (slug: \\"$TEAM\\") {
          name
          repositories (first: 100 $AFTER) {
            edges {
              node {
                name
                pullRequests (first: 100 states: OPEN) {
                  edges {
                    node {
                      title
                      url
                      author {
                        login
                      }
                      createdAt
                      reviewDecision
                    }
                  }
                }
              }
            }
            pageInfo {
              endCursor
              hasNextPage
            }
          }
        }
      }
    }"
    }"""
    if end_cursor != "":
        graph_query = graph_query.replace("$AFTER", "after: " + end_cursor)
    else:
        graph_query = graph_query.replace("$AFTER", "")

    return graph_query.replace('\n', '')\
        .replace("$ORGANIZATION", organization)\
        .replace("$TEAM", team)


def fetch_github_info(complete_query):
    url = "https://api.github.com/graphql"
    token = keyring.get_password(SERVICE_AND_USER, SERVICE_AND_USER)
    headers = {"Authorization": "Bearer " + token,
               "Content-Type": "application/json"}
    return requests.post(url, data=complete_query, headers=headers)


def extract_pr_info(pr_url):
    pr_url = pr_url.replace("https://github.com/", "")
    pr_info = pr_url.split("/")
    pr_info.pop(2)
    return pr_info


def approve_pr(pr_url):
    pr_info = extract_pr_info(pr_url)
    endpoint = "https://api.github.com/repo/{owner}/{repo}/pulls/{pull_nr}/reviews"
    endpoint.format(owner= pr_info[0], repo= pr_info[1], pull_nr= pr_info[2])
    token = keyring.get_password(SERVICE_AND_USER, SERVICE_AND_USER)
    headers = {"Authorization": "Bearer " + token,
               "Accept": "application/vnd.github.v3+json"}
    body = "{\"event\": \"APPROVE\"}"
    return requests.post(endpoint, data=body, headers=headers)


def convert_response(repos):
    converted_pr_list = []
    for repo in repos:
        name = repo["node"]["name"]
        prs = repo["node"]["pullRequests"]["edges"]
        for pr_node in prs:
            pr = pr_node["node"]
            pr["name"] = name
            pr["user"] = pr["author"]["login"]
            pr.pop("author")
            converted_pr_list.append(pr)
    return converted_pr_list


def print_header():
    print("PR".ljust(TITLE_WIDTH - 2) +
          "| URL".ljust(URL_WIDTH) +
          "| Repository".ljust(REPO_WIDTH) +
          "| Author".ljust(AUTHOR_WIDTH) +
          "| Created".ljust(CREATED_WIDTH))
    print("=".ljust(200, '='))


def print_line(pr):
    line = pr["title"][0:TITLE_WIDTH - 2].ljust(TITLE_WIDTH) + \
           pr["url"][0:URL_WIDTH - 2].ljust(URL_WIDTH) + \
           pr["name"][0:REPO_WIDTH - 2].ljust(REPO_WIDTH) + \
           pr["user"][0:AUTHOR_WIDTH - 2].ljust(AUTHOR_WIDTH) + \
           pr["createdAt"][0:CREATED_WIDTH] + \
           pr["reviewDecision"]
    print(line)


def parse_arguments():
    parser.add_argument("-T", "--token", nargs='?', type=str, help="Update personal token")
    parser.add_argument("-o", "--organization", nargs='?', type=str, help="Update organization")
    parser.add_argument("-t", "--team", nargs='?', type=str, help="Update team")
    parser.add_argument("-s", "--sort", nargs='?', type=str, default="createdAt",
                        help="What to sort by (createdAt,repo,user). Default: createdAt")
    return parser.parse_args()


def write_configuration():
    global config_file
    with open(PROPERTIES_FILE, 'wb') as config_file:
        configs[ORGANIZATION] = args.organization
        configs[TEAM] = args.team
        configs.store(config_file, encoding="utf-8")


def exit_if_config_not_set():
    if args.organization is None or args.team is None:
        print("No configuration found or incomplete setup. Please enter both organization & team")
        parser.print_usage()
        sys.exit(1)


####################################################################################
#
#  MAIN
#
####################################################################################

parser = argparse.ArgumentParser()
args = parse_arguments()
configs = Properties()
if not os.path.exists("config.properties"):
    exit_if_config_not_set()
    write_configuration()
    print("Configuration updated successfully")
else:
    if args.organization is not None or args.team is not None:
        exit_if_config_not_set()
        write_configuration()
        print("Configuration updated successfully")

with open(PROPERTIES_FILE, 'rb') as config_file:
    configs.load(config_file)
    if configs.get(ORGANIZATION) is None or configs.get("team") is None:
        print("Configuration missing, please enter organization & team")
        parser.print_help()

if args.token is not None:
    yn = input("Are you sure you want to update existing token? (y/n): ")
    if yn == "y" or yn == "Y":
        keyring.set_password(SERVICE_AND_USER, SERVICE_AND_USER, args.token)

if keyring.get_password(SERVICE_AND_USER, SERVICE_AND_USER) is None:
    print("OpenPRs requires a personal github token to work. Please refer to the readme.")
    print("")
    token = getpass("Please enter personal github token: ")
    keyring.set_password(SERVICE_AND_USER, SERVICE_AND_USER, token)
    print("Token updated!")

organization = configs.get(ORGANIZATION)[0]
team = configs.get(TEAM)[0]

response = fetch_github_info(get_query())

try:
    repoData = json.loads(response.text)["data"][ORGANIZATION][TEAM]["repositories"]
    moreData = repoData["pageInfo"]["hasNextPage"]
    repos = repoData["edges"]
    while moreData:
        response = fetch_github_info(get_query(repoData["pageInfo"]["endCursor"]))
        repoData = json.loads(response.text)["data"][ORGANIZATION][TEAM]["repositories"]
        moreData = repoData["pageInfo"]["hasNextPage"]
        repos.append(repoData["edges"])

except KeyError:
    print("Unable to parse github-response. Check your config & token. Got:")
    print(response.text)
    sys.exit(1)

pr_list = convert_response(repos)

sorted_list = sorted(pr_list, key=lambda k: k[args.sort])
print_header()

for pr in sorted_list:
    print_line(pr)
    approve_pr(pr["url"])
