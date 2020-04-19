# rage: card game
authors: lumoos & pabels

server:
# verbindung zu client aufbauen
# id senden (HELLO), antwort --> name speichern
# frage client0 bei jedem client join ob spiel starten (GO), antwort --> starte spiel
# frage client0 ob von oben oder unten (MODE), antwort --> setze spielmodus
# deck erstellen
# bestimme startspieler s
# create stats
# runden startspieler w = s
# für c in 1-10:
	# teile c karten aus
	# solange noch jemand eine karte hat
		# für client ab w:
			# broadcasten {BOARD=str TURN=int CARDS=str STATS=dict} (BOARD)
			# wenn ! stiche angesagt: antwort --> stiche 
			# sonst: antwort --> gespielte karte
		# bestimme sieger des stichs --> neues w
		# speicher stich in statistik
	# speicher runde in statistik
	# s ++ % num
# bradcast statistik (END)


logik:
- bestimme sieger des stichs
# deck erstellen



client:
# mit server verbinden
# on HELLO: name lokal speichern, name als antwort (HELLO)
# on MODE: 1-10 btn 10-1 btn, click als antwort (MODE)
# on GO: 1 wenn starten sonst 0 als antwort (GO)
# on BOARD: msg, mögliche --> gui, click als antwort (MOVE)
# on END: msg --> gui
- mögliche


gui:
- board --> card
- turn --> pfeil
- cards --> list of cards
- statistic --> tabelle
- mögliche --> andere nicht clickable
- end --> show end table with highlights
