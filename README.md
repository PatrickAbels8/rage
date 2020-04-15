# rage: card game
authors: lumoos & pabels

server:
- verbindung zu client aufbauen
- name senden (HELLO)
- frage client0 ob von oben oder unten (MODE)
- frage client0 bei jedem client join ob spiel starten (GO)
- deck erstellen
- bestimme startspieler s
- für c in 1-10:
	- teile karten aus
	- runden startspieler w = s
	- solange noch jemand eine karte hat
		- für client ab w:
			- broadcasten BOARD TURN CARDS STATISTIC (BOARD)
			- wenn ! stiche angesagt: antwort --> stiche 
			- sonst: antwort --> gespielte karte
		- bestimme sieger des stichs --> neues w
		- speicher stich in statistik
	- speicher runde in statistik
	- s ++ % num
- bradcast statistik (END)


logik:
- bestimme sieger des stichs
- speicher stich
- speicher runde



client:
- mit server verbinden
- on HELLO: name lokal speichern
- on MODE: 1-10 btn 10-1 btn, click als antwort
- on GO: 1 wenn starten sonst 0 als antwort
- on BOARD: msg, mögliche --> gui, click als antwort
- mögliche
- on END: msg --> gui


gui:
- board --> card
- turn --> pfeil
- cards --> list of cards
- statistic --> tabelle
- mögliche --> andere nicht clickable
- end --> show end table with highlights
