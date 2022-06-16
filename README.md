# Monopoli: Un’intelligenza artificiale con cui giocare

Usage: ./FQLmain.py (options) episodes gamma alpha ee_rate

options:
  
-l --load                 carica i dati della tabella q e le statistiche dell'interazione dal file .tar.gz

-s --save [save_step]     salva i dati ogni "save_step" episodi

-p --plot                 plotta le statistiche

-r --render               renderizza il gioco

--no_log                  non mostra i log dell'interazione con l'ambiente
