#!/bin/bash
set -a
source /etc/doorOpener/.env
set +a

source $SOURCEPATH/.venv/bin/activate

ERRORRUNS=0

TMPNAME="/tmp/tmp-$RANDOM"
echo "$TMPNAME"
echo "$URL?api-key=$APIKEY&actor-id=$ACTORID"

while true; do
  curl -s --connect-timeout 3 "$URL/api/getState?api-key=$APIKEY&actor-id=$ACTORID" > $TMPNAME
  if [ $? -eq 0 ] ; then
    cat $TMPNAME | python $SOURCEPATH/sh/util/check_json_state.py
    PYTHONEXIT=$?
    if [ $PYTHONEXIT -eq 0 ] ; then
      echo "true"
      python3 $SOURCEPATH/sh/util/smtp_send.py "ACTOR info: $ACTORNAME activated" "ACTOR_ID: $ACTORID TIMESTAMP: $(date +'%Y-%m-%d_%H-%M-%S')" && echo "mail sent"
      python3 $SOURCEPATH/sh/actor/activate_doorstrike.py
    elif [ $PYTHONEXIT -eq 1 ] ; then
      :
      #echo "false"
    else
      echo "error"
      let "ERRORRUNS=ERRORRUNS+1"
      echo "$ERRORRUNS"
      if [ $(($ERRORRUNS % $NOTIFYAFTER)) == 0 ] ; then
        python3 $SOURCEPATH/sh/util/smtp_send.py "SERVER Error:  $ACTORNAME curl error no. $ERRORRUNS" "ACTOR_ID: $ACTORID TIMESTAMP: $(date +'%Y-%m-%d_%H-%M-%S')" && echo "mail sent"
      fi
    fi
  else
    echo "error"
    let "ERRORRUNS=ERRORRUNS+1"
    if [ $(($ERRORRUNS % $NOTIFYAFTER)) == 0 ] ; then
      python3 $SOURCEPATH/sh/util/smtp_send.py "SERVER Error: $ACTORNAME curl error no. $ERRORRUNS" "ACTOR_ID: $ACTORID TIMESTAMP: $(date +'%Y-%m-%d_%H-%M-%S')" && echo "mail sent"
    fi
  fi
  sleep 1
done
rm $TMPNAME
exit
