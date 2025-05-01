
"""
commands.py contiene la lista di tutti i comandi che il bot può eseguire e che vengono resi visibili se
si usa il comando /help.
"""

# lista dei comandi disponibili dal bot e la loro descrizione. E' usata da /help
commands = {
    "/help": "Mostra l'elenco dei comandi",
    "/info": "Informazioni sul progetto Smart Plant",
    "/assistance": "Contatta l'assistenza in caso di problemi",
    "/login": "Accedi con username e password",
    "/register": "Crea un nuovo account",
    "/add_plant": "Aggiungi una nuova pianta al tuo smart pot",
    "/remove_plant": "Rimuovi una pianta esistente",
    "/modify_plant": "Modifica i parametri della pianta (nome, soil, temperature, humidity)",
    "/info_plant": "Restituisce le info della pianta salvata",
    "/get_data_now": "Restituisce le misurazioni della pianta in questo esatto momento",
    "/get_data": "Restituisce le misurazioni della pianta in un momento specifico",
    "/stat_plant": "Mostra le informazioni statistiche della pianta negli ultimi 7 giorni"
}
