#!/bin/bash

# $1 actor id
# $2 actor name

ACTORID=$1
ACTORNAME=$2

# DOOROPENER CONFIG
set -a
source /etc/doorOpener/.env_server
set +a
source $SOURCEPATH/.venv/bin/activate

ERRORRUNS=0

TMPNAME="/tmp/tmp-$RANDOM"
echo "$TMPNAME"
echo "$URL/api/actorHealth?api-key=$APIKEY&actor-id=$ACTORID&timeout=$TIMEOUT"

while true; do
  curl --connect-timeout 3 "$URL/api/actorHealth?api-key=$APIKEY&actor-id=$ACTORID&timeout=$TIMEOUT" > $TMPNAME
  if [ $? -eq 0 ] ; then
    cat $TMPNAME
    cat $TMPNAME | python $SOURCEPATH/sh/util/check_json_health.py
    if [ $? -eq 0 ] ; then
      :
    elif [ $? -eq 1 ] ; then
      echo "actor timeout"
      let "ERRORRUNS=ERRORRUNS+1"
      if [ $(($ERRORRUNS % $NOTIFYAFTER)) == 0 ] ; then
        python $SOURCEPATH/sh/util/smtp_send.py "ACTOR Error: $ACTORNAME curl error no. $ERRORRUNS" "SERVER ACTOR_ID: $ACTORID TIMESTAMP: $(date +'%Y-%m-%d_%H-%M-%S')"
      fi
    else
      echo "error"
      let "ERRORRUNS=ERRORRUNS+1"
      if [ $(($ERRORRUNS % $NOTIFYAFTER)) == 0 ] ; then
        python $SOURCEPATH/sh/util/smtp_send.py "ACTOR Error: $ACTORNAME curl error no. $ERRORRUNS" "SERVER ACTOR_ID: $ACTORID TIMESTAMP: $(date +'%Y-%m-%d_%H-%M-%S')"
      fi
    fi
  else
    echo "error"
    let "ERRORRUNS=ERRORRUNS+1"
    if [ $(($ERRORRUNS % $NOTIFYAFTER)) == 0 ] ; then
      python $SOURCEPATH/sh/util/smtp_send.py "HEALTHCHECK Error: $ACTORNAME curl error no. $ERRORRUNS" "SERVER ACTOR_ID: $ACTORID TIMESTAMP: $(date +'%Y-%m-%d_%H-%M-%S')"
    fi
  fi
  sleep $INTERVAL
done
rm $TMPNAME
