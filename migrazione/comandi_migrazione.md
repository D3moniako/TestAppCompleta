
# Esempio di creazione di una migrazione
$ alembic revision --autogenerate -m "Descrizione della migrazione"

# Esempio di applicazione di una migrazione
$ alembic upgrade head




1. **Listare le Migrazioni:**
   ```bash
   alembic history
   ```

   Questo comando ti mostrerà un elenco di tutte le migrazioni applicate, con i loro ID.

2. **Torna a una Migrazione Specifica:**
   ```bash
   alembic downgrade <migration_id>
   ```

   Sostituisci `<migration_id>` con l'ID della migrazione a cui desideri tornare. Questo comando farà il downgrade della tua base di dati alla versione precedente.

3. **Applica Migrazioni Successive:**
   ```bash
   alembic upgrade head
   ```

   Se desideri tornare alla versione più recente dopo essere andato indietro, puoi utilizzare questo comando per applicare tutte le migrazioni successivamente alla versione corrente.

È una buona pratica testare attentamente le migrazioni e mantenere una documentazione chiara delle modifiche apportate a ciascuna migrazione. Inoltre, considera l'opzione di eseguire backup del tuo database prima di applicare migrazioni significative, specialmente in un ambiente di produzione.