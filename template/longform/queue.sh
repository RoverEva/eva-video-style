#!/bin/bash
# sequential render queue: each line of queue.txt = script|zh_out|en_out ; finished lines are appended to queue.done
cd "$(dirname "$0")/../.."
Q=template/longform/queue.txt; D=template/longform/queue.done
touch $D
while true; do
  job=$(grep -vxF -f $D $Q 2>/dev/null | head -1)
  if [ -z "$job" ]; then sleep 30; continue; fi
  IFS='|' read -r s zh en <<< "$job"
  name=$(basename "$s" .txt); mkdir -p /tmp/parts_$name
  echo "[$(date +%H:%M)] start $name" >> /tmp/queue.log
  python3 template/longform/long_sign.py "$s" --out "$zh" --out-en "$en" --parts /tmp/parts_$name >> /tmp/queue_$name.log 2>&1
  if [ -f "$zh" ] && [ -f "$en" ]; then echo "$job" >> $D; rm -rf /tmp/parts_$name; echo "[$(date +%H:%M)] done $name" >> /tmp/queue.log
  else echo "[$(date +%H:%M)] FAIL $name" >> /tmp/queue.log; echo "$job" >> $D; fi
done
