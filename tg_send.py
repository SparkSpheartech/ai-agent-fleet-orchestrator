import re, urllib.request, json, sys
home = "/home/%s" % sys.argv[1] if len(sys.argv) > 1 else "/root"
chat_arg = sys.argv[2] if len(sys.argv) > 2 else None
# message from stdin (handles multiline safely)
msg = sys.stdin.read().strip()
env = open(home + "/.hermes/.env").read()
tok = re.search(r"TELEGRAM_BOT_TOKEN=(\S+)", env).group(1)
chat = chat_arg or re.search(r"TELEGRAM_HOME_CHANNEL=(\S+)", env).group(1)
data = json.dumps({"chat_id": chat, "text": msg}).encode()
req = urllib.request.Request("https://api.telegram.org/bot"+tok+"/sendMessage", data, {"Content-Type":"application/json"})
try:
    resp = urllib.request.urlopen(req, timeout=15).read().decode()
    print("SENT_OK" if '"ok":true' in resp else "SEND_FAIL:"+resp[:100])
except Exception as e:
    print("SEND_ERR:"+str(e)[:100])
