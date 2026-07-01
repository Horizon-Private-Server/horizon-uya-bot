#!/bin/bash
QUEUE_DIR="$HOME/Development/PS2/HV2Server/horizon-runtime/plugins/medius/bot_queue"
BOT_DIR="$HOME/Development/PS2/HV2Server/horizon-uya-bot"
mkdir -p "$QUEUE_DIR"

# Detect terminal for visual bot output
TERM_CMD=""
for t in alacritty foot kitty gnome-terminal xterm; do
    if command -v $t &>/dev/null; then TERM_CMD="$t"; break; fi
done

echo "HV2 Bot Watcher - watching $QUEUE_DIR"
echo "Invite bots from in-game patch menu. Ctrl+C to stop."

while true; do
    for f in "$QUEUE_DIR"/*.json; do
        [ -f "$f" ] || continue
        BOT_NAME=$(basename "$f" .json)
        echo "=== Spawning $BOT_NAME ==="
        DATA=$(cat "$f")
        rm -f "$f"
        CFG="/tmp/hv2-bot-$(date +%s).json"
        LOG="/tmp/hv2-bot-$BOT_NAME.log"
        python3 -c "
import json
t = json.loads('''$DATA''')
cfg = {
    'local': True,
    'profile_id': t.get('profile_id') or 50,
    'bot_mode': t.get('bot_mode', 'dynamic'),
    'account_id': 9001,
    'account_name': 'bot1',
    'password': 'botpass',
    'world_id': t['world_id'],
    'mas_ip': '10.0.0.49', 'mas_port': 10075,
    'mls_ip': '10.0.0.49', 'mls_port': 10078,
    'timeout': 240,
    'mls_log_level': 'info', 'mas_log_level': 'info',
    'dmetcp_log_level': 'info', 'dmeudp_log_level': 'info',
    'model_log_level': 'info',
    'game_name_to_join': ''
}
with open('$CFG', 'w') as fh:
    json.dump(cfg, fh)
"
        BOT_CMD="cd '$BOT_DIR' && python3 thug.py --config '$CFG'; echo '--- Done (closing in 5s) ---'; sleep 5"
        if [ -n "$TERM_CMD" ]; then
            case "$TERM_CMD" in
                alacritty) alacritty -e bash -c "$BOT_CMD" & ;;
                foot)       foot bash -c "$BOT_CMD" & ;;
                kitty)      kitty bash -c "$BOT_CMD" & ;;
                gnome-terminal) gnome-terminal -- bash -c "$BOT_CMD" & ;;
                xterm)      xterm -e "$BOT_CMD" & ;;
            esac
        else
            nohup bash -c "$BOT_CMD > '$LOG' 2>&1" &
        fi
        # Small delay to let server finalize game creation
        sleep 3
    done
    sleep 2
done
