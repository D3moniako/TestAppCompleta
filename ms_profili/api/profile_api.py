from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from repository import UserProfileRepository, StatisticsRepository, ImageRepository
from db.engine import get_db
from db.modelli import Profile, MusicPreferences, SportPreferences, Image, ProfileAccess
from typing import List
from confluent_kafka import Consumer, KafkaException, KafkaError

router = APIRouter()

user_profile_repo = UserProfileRepository()
statistics_repo = StatisticsRepository()
image_repo = ImageRepository()

###kafka ###
###kafka ###
kafka_bootstrap_servers = "kafka:9092"
consumer = Consumer({
    'bootstrap.servers': kafka_bootstrap_servers,
    'group.id': 'profile_group',
    'auto.offset.reset': 'earliest'  # Configurazione per leggere tutti gli eventi dalla coda
})

# Sottoscrivi il consumatore alla coda 'user_events'
consumer.subscribe(['user_events'])


async def consume_user_events():
    while True:
        msg = consumer.poll(1000)  # Imposta il timeout della poll a 1 secondo
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # La fine della partizione è normale e può essere ignorata
                continue
            else:
                raise KafkaException(msg.error())
        # Processa l'evento
        event_data = json.loads(msg.value().decode('utf-8'))
        await handle_user_created_event(event_data)


async def handle_user_created_event(event_data: dict, db: Session = Depends(get_db)):
    try:
        # Estrai i dati dall'evento
        username = event_data.get("username", "")

        # Esempio: controlla se il profilo esiste già
        existing_profile = user_profile_repo.get_user_profile_by_username(db, username)
        if existing_profile:
            # Se il profilo esiste già, puoi gestire questo caso come desideri
            return {"message": "Il profilo esiste già"}

        # Esempio: crea un profilo di base
        profile = user_profile_repo.create_user_profile(
            db,
            first_name="",
            second_name="",
            hobby="",
            music=[],
            sport=[],
            bio="",
            user_id=0,  # Sostituisci con l'ID dell'utente associato
            website=""
        )

        return {"message": "Profilo creato con successo", "profile": profile}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Avvia il consumatore Kafka come un'attività asincrona
asyncio.create_task(consume_user_events())





@router.post("/user-profile", response_model=Profile)
def create_user_profile(
    first_name: str, 
    second_name: str, 
    hobby: str, 
    music: list, 
    sport: list, 
    bio: str, 
    user_id: int, 
    website: str,
    db: Session = Depends(get_db)
):
    try:
        return user_profile_repo.create_user_profile(
            db, first_name, second_name, hobby, music, sport, bio, user_id, website
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/user-profile/{username}", response_model=Profile)
def get_user_profile_by_username(username: str, db: Session = Depends(get_db)):
    try:
        profile = user_profile_repo.get_user_profile_by_username(db, username)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile not found for username {username}"
            )
        return profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/user-profile/{username}", response_model=Profile)
def update_user_profile(
    username: str, 
    updated_profile: dict, 
    db: Session = Depends(get_db)
):
    try:
        profile = user_profile_repo.update_user_profile(db, username, updated_profile)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile not found for username {username}"
            )
        return profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/user-profile/{username}")
def delete_user_profile(username: str, db: Session = Depends(get_db)):
    try:
        result = user_profile_repo.delete_user_profile(db, username)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile not found for username {username}"
            )
        return {"message": f"Profile for username {username} deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

###
# Continuazione da dove ci eravamo interrotti

@router.get("/user-profile/id/{profile_id}", response_model=Profile)
def get_user_profile_by_id(profile_id: int, db: Session = Depends(get_db)):
    try:
        profile = user_profile_repo.get_user_profile_by_id(db, profile_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile not found for ID {profile_id}"
            )
        return profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/user-profiles", response_model=List[Profile])
def get_all_user_profiles(db: Session = Depends(get_db)):
    try:
        profiles = user_profile_repo.get_all_user_profiles(db)
        return profiles
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/music-preferences/{user_id}")
def update_music_preferences(user_id: int, music_preferences: List[str], db: Session = Depends(get_db)):
    try:
        user_profile_repo.update_music_preferences(db, user_id, music_preferences)
        return {"message": "Music preferences updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/sport-preferences/{user_id}")
def update_sport_preferences(user_id: int, sport_preferences: List[str], db: Session = Depends(get_db)):
    try:
        user_profile_repo.update_sport_preferences(db, user_id, sport_preferences)
        return {"message": "Sport preferences updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/profile-access", response_model=ProfileAccess)
def log_profile_access(user_id: int, db: Session = Depends(get_db)):
    try:
        return statistics_repo.log_profile_access(db, user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/music-preferences/{user_id}", response_model=List[str])
def get_music_preferences(user_id: int, db: Session = Depends(get_db)):
    try:
        music_prefs = statistics_repo.get_music_preferences(db, user_id)
        return music_prefs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Continuazione e completamento delle API con controlli tramite eccezioni

@router.get("/sport-preferences/{user_id}", response_model=List[str])
def get_sport_preferences(user_id: int, db: Session = Depends(get_db)):
    try:
        sport_prefs = statistics_repo.get_sport_preferences(db, user_id)
        return sport_prefs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/profile-access/{user_id}", response_model=List[ProfileAccess])
def get_profile_access_by_user_id(user_id: int, db: Session = Depends(get_db)):
    try:
        profile_access = statistics_repo.get_profile_access_by_user_id(db, user_id)
        return profile_access
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/total-profile-access", response_model=int)
def get_total_profile_access(db: Session = Depends(get_db)):
    try:
        total_access = statistics_repo.get_total_profile_access(db)
        return total_access
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/all-music-preferences", response_model=List[MusicPreferences])
def get_all_music_preferences(db: Session = Depends(get_db)):
    try:
        all_music_prefs = statistics_repo.get_all_music_preferences(db)
        return all_music_prefs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/all-sport-preferences", response_model=List[SportPreferences])
def get_all_sport_preferences(db: Session = Depends(get_db)):
    try:
        all_sport_prefs = statistics_repo.get_all_sport_preferences(db)
        return all_sport_prefs
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/upload-image", response_model=Image)
def upload_image(user_id: int, name: str, url: str, state: int, source: str, db: Session = Depends(get_db)):
    try:
        return image_repo.upload_image(db, user_id, name, url, state, source)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/user-images/{user_id}", response_model=List[Image])
def get_user_images(user_id: int, db: Session = Depends(get_db)):
    try:
        user_images = image_repo.get_user_images(db, user_id)
        return user_images
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

