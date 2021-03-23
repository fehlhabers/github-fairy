import requests
import sys

query = """{ "query" : "query {
      rateLimit {
        limit
        cost
        remaining
        resetAt
      }
      organization (login: 'ORGANIZATION') {
        name
        team (slug: 'TEAM') {
          name
          repositories (first: 100 ) {
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

organization = sys.argv[1]
team = sys.argv[2]

query = query.replace('\n', '')
query = query.replace("'", "\\\"")

query = query.replace("ORGANIZATION", organization)
query = query.replace("TEAM", team)

url = "https://api.github.com/graphql"

token = sys.stdin.read()
headers = {"Authorization": "Bearer " + token,
           "Content-Type": "application/json"}

response = requests.post(url, data=query, headers=headers)
print(response.text)