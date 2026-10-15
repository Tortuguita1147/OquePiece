#!/bin/bash
cd /home/user/workspaces/732db4c0-b54e-45f4-9dee-4b4e0b61e684/oquepiece
python3 app.py > /tmp/flask.log 2>&1 &
PID=$!
sleep 4
BASE=http://127.0.0.1:5000
ROTAS="/ /personagens /wordle /piramide /grid /maior-menor /connections /bingo /wanted /fruta /jolly-roger /impostor /identidade /risa /sopa /episodio /draft /api/personagens"
FALHAS=0
for r in $ROTAS; do
  CODE=$(curl -s -o /tmp/page.html -w "%{http_code}" "$BASE$r")
  if [ "$CODE" != "200" ]; then echo "FALHA $r -> HTTP $CODE"; FALHAS=$((FALHAS+1)); fi
  if grep -q "Traceback (most recent call last)" /tmp/page.html; then echo "TRACEBACK em $r"; FALHAS=$((FALHAS+1)); fi
done
echo "Rotas testadas: $(echo $ROTAS | wc -w) | Falhas: $FALHAS"
echo "--- log do flask ---"; tail -5 /tmp/flask.log
kill $PID 2>/dev/null
