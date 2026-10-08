from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Tag(BaseModel):
    model_config = ConfigDict(extra="ignore")

    term: str


class MetObject(BaseModel):
    model_config = ConfigDict(extra="ignore")

    objectID: int = Field(gt=0)
    title: str
    department: str
    objectDate: str
    objectBeginDate: int
    objectEndDate: int
    accessionNumber: str
    isHighlight: bool
    isPublicDomain: bool
    objectURL: str

    artistDisplayName: str = ""
    objectName: str = ""
    culture: str = ""
    period: str = ""
    medium: str = ""
    classification: str = ""
    creditLine: str = ""
    primaryImage: str = ""
    primaryImageSmall: str = ""
    additionalImages: List[str] = Field(default_factory=list)
    tags: Optional[List[Tag]] = None
    GalleryNumber: str = ""

    @field_validator("objectURL")
    @classmethod
    def url_must_point_to_met(cls, value: str) -> str:
        if not value.startswith("https://www.metmuseum.org/"):
            raise ValueError(
                f"objectURL должен вести на metmuseum.org: {value!r}"
            )
        return value


class ObjectIDsResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    total: int = Field(ge=0)
    objectIDs: List[int] = Field(default_factory=list)

    @field_validator("objectIDs", mode="before")
    @classmethod
    def null_to_empty_list(cls, value):
        return [] if value is None else value