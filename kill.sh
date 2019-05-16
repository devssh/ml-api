kill $(ps aux | grep curl | grep -v grep | awk '{print $2}')
