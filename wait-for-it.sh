#!/bin/bash
# wait-for-it.sh - Wait for service to be available

set -e

host="$1"
port="$2"
shift 2
cmd="$@"

echo "Waiting for $host:$port..."

until nc -z "$host" "$port"; do
  >&2 echo "$host:$port is unavailable - sleeping"
  sleep 1
done

>&2 echo "$host:$port is up - executing command"
exec $cmd
