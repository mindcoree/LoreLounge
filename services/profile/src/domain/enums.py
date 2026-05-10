from enum import Enum


class GenderEnum(str, Enum):
    UNSPECIFIED = "unspecified"
    MALE = "male"
    FEMALE = "female"