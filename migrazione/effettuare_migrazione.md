
                MIGRAZIONE
1. **Modifica il Modello:** Apporta le modifiche necessarie al modello del tuo database. Ad esempio, aggiungi o modifica campi nelle tabelle.

2. **Salva il Codice:** Dopo aver apportato le modifiche al modello, salva il tuo codice.

3. **Genera la Migrazione:** Utilizza gli strumenti forniti dal tuo ORM o dal sistema di migrazione per generare uno script di migrazione basato sulle modifiche apportate al modello. Questo script descriverà come il tuo database dovrebbe essere aggiornato per riflettere il nuovo modello.

4. **Applica la Migrazione:** Esegui lo script di migrazione per apportare effettivamente le modifiche al tuo database. Questo potrebbe coinvolgere l'utilizzo di comandi specifici del tuo ORM o di strumenti di migrazione come Alembic.

5. **Run del Progetto:** Riavvia il tuo progetto. Ciò consente al tuo codice di utilizzare il nuovo modello di database.

6. **Test:** Esegui i test per assicurarti che il tuo progetto funzioni correttamente con il nuovo modello di database. Questo include test automatici, test manuali o entrambi.

7. **Verifica il Funzionamento:** Controlla manualmente che le nuove funzionalità o modifiche al modello di database abbiano effetto come previsto. Verifica che i dati vengano salvati e recuperati correttamente, e che il tuo progetto funzioni senza errori.

8. **Ambiente di Sviluppo vs. Produzione:** Esegui questi passaggi inizialmente in un ambiente di sviluppo per risolvere eventuali problemi. Una volta confermato che tutto funziona correttamente, puoi poi applicare le modifiche a un ambiente di produzione. Assicurati di avere backup del database prima di apportare modifiche in produzione.







Alembic salva le informazioni sulla history e le migrazioni in una directory denominata `alembic` all'interno del tuo progetto. All'interno di questa directory, ci saranno diversi file e cartelle generati da Alembic:

1. **alembic.ini:** Questo file di configurazione contiene le informazioni di configurazione per Alembic, come il percorso del database e altre opzioni.

2. **env.py:** Questo file contiene la configurazione dell'ambiente per Alembic, incluso il percorso del database e l'oggetto `target_metadata` che definisce i modelli del database.

3. **versions:** Questa cartella contiene i file di migrazione numerati. Ogni file ha un nome univoco formato da un timestamp e un breve descrizione della migrazione. Ad esempio, `1234567890123_add_column.py`.

4. **alembic.sqlite**: Questa cartella può essere presente se stai utilizzando SQLite come database. Contiene informazioni di tracciamento specifiche per SQLite.

Il file `alembic.ini` e `env.py` vengono utilizzati per configurare l'ambiente di migrazione di Alembic, mentre la cartella `versions` contiene gli script di migrazione reali. Alembic traccia lo stato delle migrazioni applicate nel database utilizzando una tabella speciale chiamata `alembic_version`, che è creata automaticamente la prima volta che esegui una migrazione. Questa tabella contiene un singolo record che rappresenta la versione attuale del database in termini di migrazioni applicate.

In breve, la struttura della cartella `alembic` è gestita da Alembic stesso per tenere traccia delle migrazioni e delle informazioni sulla storia.




# alembic.ini

# ...
# Questa opzione specifica il percorso della cartella alembic
# script_location = alembic
script_location = my_migration_folder
