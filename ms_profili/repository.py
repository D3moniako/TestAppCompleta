from sqlalchemy.orm import Session
from db.modelli import Profile, Image, SportPreferences, MusicPreferences, ProfileAccess
from fastapi import HTTPException, status
from typing import List, Optional


class UserProfileRepository:
    def create_user_profile(self, db: Session, first_name: str, second_name: str, hobby: str, music: list, sport: list, bio: str, user_id: int, website: str) -> Profile:
        """
        Crea un nuovo profilo utente nel database.

        :param db: Sessione del database.
        :param first_name: Nome dell'utente.
        :param second_name: Cognome dell'utente.
        :param hobby: Hobby dell'utente.
        :param music: Lista delle preferenze musicali dell'utente.
        :param sport: Lista delle preferenze sportive dell'utente.
        :param bio: Biografia dell'utente.
        :param user_id: ID dell'utente associato al profilo.
        :param website: Sito web dell'utente.
        :return: Oggetto del profilo utente creato.
        """
        user_profile = Profile(
            first_name=first_name,
            second_name=second_name,
            hobby=hobby,
            music=music,
            sport=sport,
            bio=bio,
            user_id=user_id,
            website=website
        )
        db.add(user_profile)
        db.commit()
        db.refresh(user_profile)
        return user_profile

    def get_user_profile_by_username(self, db: Session, username: str) -> Profile:
        """
        Ottiene il profilo utente basato sul nome utente.

        :param db: Sessione del database.
        :param username: Nome utente.
        :return: Oggetto del profilo utente.
        """
        return db.query(Profile).filter(Profile.username == username).first()

    def get_user_profile_by_id(self, db: Session, profile_id: int) -> Profile:
        """
        Ottiene il profilo utente basato sull'ID del profilo.

        :param db: Sessione del database.
        :param profile_id: ID del profilo utente.
        :return: Oggetto del profilo utente.
        """
        return db.query(Profile).filter(Profile.id == profile_id).first()

    def update_user_profile(self, db: Session, username: str, updated_profile: dict):
        """
        Aggiorna il profilo utente.

        :param db: Sessione del database.
        :param username: Nome utente.
        :param updated_profile: Dizionario contenente i dati aggiornati del profilo.
        :return: Messaggio di successo o eccezione.
        """
        user_profile = self.get_user_profile_by_username(db, username)
        if user_profile:
            for key, value in updated_profile.items():
                setattr(user_profile, key, value)
            db.commit()
            db.refresh(user_profile)
            return {"message": "Profilo utente aggiornato con successo"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profilo utente non trovato per {username}",
            )

    def delete_user_profile(self, db: Session, username: str):
        """
        Cancella il profilo utente.

        :param db: Sessione del database.
        :param username: Nome utente.
        :return: Messaggio di successo o eccezione.
        """
        user_profile = self.get_user_profile_by_username(db, username)
        if user_profile:
            db.delete(user_profile)
            db.commit()
            return {"message": f"Profilo utente per {username} cancellato con successo"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profilo utente non trovato per {username}",
            )

    def get_all_user_profiles(self, db: Session) -> List[Profile]:
        """
        Ottiene tutti i profili utente presenti nel sistema.

        :param db: Sessione del database.
        :return: Lista di oggetti dei profili utente.
        """
        return db.query(Profile).all()

    def update_music_preferences(self, db: Session, user_id: int, music_preferences: List[str]):
        """
        Aggiorna le preferenze musicali dell'utente.

        :param db: Sessione del database.
        :param user_id: ID dell'utente.
        :param music_preferences: Lista delle preferenze musicali dell'utente.
        """
        db.query(MusicPreferences).filter(MusicPreferences.user_id == user_id).delete()
        for genre in music_preferences:
            db_music_preferences = MusicPreferences(user_id=user_id, music_genre=genre)
            db.add(db_music_preferences)
        db.commit()

    def update_sport_preferences(self, db: Session, user_id: int, sport_preferences: List[str]):
        """
        Aggiorna le preferenze sportive dell'utente.

        :param db: Sessione del database.
        :param user_id: ID dell'utente.
        :param sport_preferences: Lista delle preferenze sportive dell'utente.
        """
        db.query(SportPreferences).filter(SportPreferences.user_id == user_id).delete()
        for sport in sport_preferences:
            db_sport_preferences = SportPreferences(user_id=user_id, favorite_sport=sport)
            db.add(db_sport_preferences)
        db.commit()


class StatisticsRepository:
    def log_profile_access(self, db: Session, user_id: int):
        """
        Registra l'accesso al profilo utente.

        :param db: Sessione del database.
        :param user_id: ID dell'utente.
        :return: Oggetto di accesso al profilo registrato.
        """
        profile_access = ProfileAccess(user_id=user_id)
        db.add(profile_access)
        db.commit()
        db.refresh(profile_access)
        return profile_access

    def get_profile_access_by_user_id(self, db: Session, user_id: int) -> List[ProfileAccess]:
        """
        Ottiene le statistiche di accesso del profilo utente basate sull'ID dell'utente.

        :param db: Sessione del database.
        :param user_id: ID dell'utente.
        :return: Lista di oggetti di accesso al profilo.
        """
        return db.query(ProfileAccess).filter(ProfileAccess.user_id == user_id).all()

    def get_total_profile_access(self, db: Session) -> int:
        """
        Ottiene il conteggio totale degli accessi al profilo.

        :param db: Sessione del database.
        :return: Numero totale di accessi al profilo.
        """
        return db.query(ProfileAccess).count()

    def get_all_music_preferences(self, db: Session) -> List[MusicPreferences]:
        """
        Ottiene le preferenze musicali di tutti gli utenti.

        :param db: Sessione del database.
        :return: Lista di oggetti delle preferenze musicali.
        """
        return db.query(MusicPreferences).all()

    def get_all_sport_preferences(self, db: Session) -> List[SportPreferences]:
        """
        Ottiene le preferenze sportive di tutti gli utenti.

        :param db: Sessione del database.
        :return: Lista di oggetti delle preferenze sportive.
        """
        return db.query(SportPreferences).all()


class ImageRepository:
    def upload_image(self, db: Session, user_id: int, name: str, url: str, state: int, source: str):
        """
        Carica un'immagine nel database.

        :param db: Sessione del database.
        :param user_id: ID dell'utente.
        :param name: Nome dell'immagine.
        :param url: URL dell'immagine.
        :param state: Stato dell'immagine.
        :param source: Fonte dell'immagine.
        :return: Oggetto dell'immagine caricata.
        """
        image = Image(user_id=user_id, name=name, url=url, state=state, source=source)
        db.add(image)
        db.commit()
        db.refresh(image)
        return image

    def get_user_images(self, db: Session, user_id: int) -> List[Image]:
        """
        Ottiene le immagini dell'utente.

        :param db: Sessione del database.
        :param user_id: ID dell'utente.
        :return: Lista di oggetti delle immagini dell'utente.
        """
        user_images = db.query(Image).filter(Image.user_id == user_id).all()
        return user_images

    def get_image_by_name(self, db: Session, user_id: int, name: str) -> Image:
        """
        Ottiene un'immagine per nome.

        :param db: Sessione del database.
        :param user_id: ID dell'utente.
        :param name: Nome dell'immagine.
        :return: Oggetto dell'immagine.
        """
        return db.query(Image).filter(Image.user_id == user_id, Image.name == name).first()

    def delete_image(self, db: Session, user_id: int, name: str):
        """
        Cancella un'immagine.

        :param db: Sessione del database.
        :param user_id: ID dell'utente.
        :param name: Nome dell'immagine.
        :return: Messaggio di successo o eccezione.
        """
        image = db.query(Image).filter(Image.user_id == user_id, Image.name == name).first()
        if image:
            db.delete(image)
            db.commit()
            return {"message": f"Immagine {name} cancellata con successo"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Immagine {name} non trovata",
            )

    def update_image(self, db: Session, user_id: int, name: str, url: str, state: int, source: str):
        """
        Aggiorna le informazioni sull'immagine.

        :param db: Sessione del database.
        :param user_id: ID dell'utente.
        :param name: Nome dell'immagine.
        :param url: URL dell'immagine.
        :param state: Stato dell'immagine.
        :param source: Fonte dell'immagine.
        """
        image = db.query(Image).filter(Image.user_id == user_id, Image.name == name).first()
        if image:
            image.url = url
            image.state = state
            image.source = source
            db.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Immagine {name} non trovata",
            )
