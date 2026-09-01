#!/bin/sh
set -eu

stop() {
  /opt/project-starter/project stop >/dev/null 2>&1 || true
  exit 0
}
trap stop INT TERM

/opt/project-starter/project start
while /opt/project-starter/project status >/dev/null 2>&1; do
  sleep 30 &
  wait $!
done
exit 1
