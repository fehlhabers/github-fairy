ORG="-"
TEAM="-"

case $1 in
"date")
  SORT_BY="createdAt"
  ;;
"repo")
  SORT_BY="name"
  ;;
"user")
  SORT_BY="user"
  ;;
*)
  echo "Usage: ./open-prs.sh [date repo user]"
  echo "Choose how to sort PRs"
  exit 2;
  ;;
esac

secret-tool lookup fehlhabers open-prs | python3 open-prs.py $ORG $TEAM $SORT_BY