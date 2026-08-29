from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, computed_field


class CertificateType(StrEnum):
    OBC_NCL = "obc_non_creamy_layer"
    EWS = "ews"
    CASTE = "caste"
    DOMICILE = "domicile"
    DISABILITY = "disability"


CERTIFICATE_LABEL: dict[CertificateType, str] = {
    CertificateType.OBC_NCL: "OBC non-creamy layer certificate",
    CertificateType.EWS: "EWS certificate",
    CertificateType.CASTE: "Caste certificate",
    CertificateType.DOMICILE: "Domicile certificate",
    CertificateType.DISABILITY: "Disability certificate",
}

MUST_BE_CURRENT_YEAR = {CertificateType.OBC_NCL, CertificateType.EWS}


def financial_year_start(day: date) -> date:
    return date(day.year if day.month >= 4 else day.year - 1, 4, 1)


class Certificate(BaseModel):
    kind: CertificateType
    issued_on: date

    def is_stale_on(self, today: date) -> bool:
        if self.kind not in MUST_BE_CURRENT_YEAR:
            return False
        return self.issued_on < financial_year_start(today)


class CertificateWarning(BaseModel):
    kind: CertificateType
    label: str
    issued_on: date
    needed_from: date

    @computed_field
    @property
    def plain_words(self) -> str:
        return (
            f"Your {self.label} is from {self.issued_on.strftime('%d %B %Y')}. "
            f"Most exams want one issued after {self.needed_from.strftime('%d %B %Y')}. "
            "Get a new one before you apply."
        )


def check_certificates(certificates: list[Certificate], today: date) -> list[CertificateWarning]:
    start = financial_year_start(today)
    return [
        CertificateWarning(
            kind=c.kind,
            label=CERTIFICATE_LABEL[c.kind],
            issued_on=c.issued_on,
            needed_from=start,
        )
        for c in certificates
        if c.is_stale_on(today)
    ]
