from typing import Optional
from pydantic import BaseModel, ConfigDict
from enum import Enum
from datetime import datetime


class RegulationType(str, Enum):
    IOSA = "IOSA"
    ECAR = "ECAR"
    GACAR = "GACAR"


RegulationTypeDefinitions = {
    RegulationType.IOSA: """The IATA Operational Safety Audit (IOSA) is a globally recognized evaluation system developed by the International Air Transport Association (IATA) to assess airlines' operational management and safety control systems. It covers various areas including flight operations, maintenance, ground handling, and security, ensuring compliance with international safety standards.""",
    RegulationType.GACAR: """GACAR is the General Civil Aviation Authority Regulations in the United Arab Emirates, likely outlines specific guidelines or standards related to aviation operations, safety, or certification processes. These regulations could cover areas such as aircraft maintenance, pilot training requirements, airworthiness standards, or operational procedures.""",
    RegulationType.ECAR: """ECAR stands for Egyptian Civil Aviation Regulations, which are the set of rules and standards governing aviation activities in Egypt. These regulations cover various aspects of aviation safety, security, operations, and maintenance to ensure compliance with international standards set by organizations like the International Civil Aviation Organization (ICAO).""",
}


class Constrain(BaseModel):
    text: str
    children: list["Constrain"] = []


class IOSAItem(BaseModel):
    code: str
    guidance: Optional[str] = None
    iosa_map: list[str] = []
    paragraph: str
    page: Optional[int] = None
    constraints: Optional[list[Constrain]] = []


class IOSASection(BaseModel):
    name: str
    code: str
    applicability: str
    guidance: Optional[str] = None
    items: list[IOSAItem]


class IOSARegulation(BaseModel):
    id: Optional[str] = None
    type: RegulationType = RegulationType.IOSA
    name: str
    effective_date: datetime
    sections: list[IOSASection]

    model_config = ConfigDict(use_enum_values=True)


class RegulationsMetaData(BaseModel):
    id: Optional[str] = None
    type: RegulationType
    name: str
    effective_date: datetime

    model_config = ConfigDict(use_enum_values=True)


class RegulationsSourceMap(BaseModel):
    code: str
    title: str
    sub_section: list[str]
    regulation_id: str
