# decoratore per gestire relazioni
from sqlmodel import Field, Relationship, create_engine

def relationship(*, sa_relationship, back_populates, nullable=False):
    return Field(
        ...,
        sa_column=sa_relationship,
        example={"id": 123, "name": "Example"},
        description="The related data.",
        foreign_key=True,
        nullable=nullable,
        python_name=back_populates,
        sa_back_populates=back_populates,
    )
