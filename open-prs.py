import requests
import sys
import json


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


query = get_query()\
    .replace("$ORGANIZATION", sys.argv[1])\
    .replace("$TEAM", sys.argv[2])

url = "https://api.github.com/graphql"

token = sys.stdin.read()
headers = {"Authorization": "Bearer " + token,
           "Content-Type": "application/json"}

response = requests.post(url, data=query, headers=headers)
jdict = json.loads(response.text)
repos = jdict["data"]["organization"]["team"]["repositories"]["edges"]

pr_list = []
for repo in repos:
    name = repo["node"]["name"]
    prs = repo["node"]["pullRequests"]["edges"]
    for pr_node in prs:
        pr = pr_node["node"]
        pr["name"] = name
        pr["user"] = pr["author"]["login"]
        pr.pop("author")
        pr_list.append(pr)
sorted_list = sorted(pr_list, key=lambda k: k["user"])
print(sorted_list)