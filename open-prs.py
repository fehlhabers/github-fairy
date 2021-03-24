import requests
import sys
import json

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
    return graph_query.replace('\n', '')


def github_request(complete_query):
    url = "https://api.github.com/graphql"
    token = sys.stdin.read()
    headers = {"Authorization": "Bearer " + token,
               "Content-Type": "application/json"}
    return requests.post(url, data=complete_query, headers=headers)


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
           pr["createdAt"][0:CREATED_WIDTH]
    print(line)


query = get_query() \
    .replace("$ORGANIZATION", sys.argv[1]) \
    .replace("$TEAM", sys.argv[2])
sort_by = sys.argv[3]

response = github_request(query)

repos = json.loads(response.text)["data"]["organization"]["team"]["repositories"]["edges"]

pr_list = convert_response(repos)
sorted_list = sorted(pr_list, key=lambda k: k[sort_by])
print_header()

for pr in sorted_list:
    print_line(pr)
