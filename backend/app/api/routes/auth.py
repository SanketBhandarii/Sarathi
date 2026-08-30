from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.auth import tokens
from app.auth.hygiene import judge
from app.auth.passwords import WeakPassword
from app.auth.service import AuthProblem, issue_code, find_user, register, sign_in, verify_code
from app.db.repositories import students as students_repo
from app.language.phrases import Language
from app.student.profile import Category, Education, Gender, StudentProfile

router = APIRouter(prefix="/auth", tags=["auth"])

SESSION_COOKIE = "sarathi_session"


class SignUpIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    language: Language = Language.ENGLISH


class CodeIn(BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class ResendIn(BaseModel):
    email: EmailStr
    language: Language = Language.ENGLISH


class SignInIn(BaseModel):
    email: EmailStr
    password: str


class ProfileIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    date_of_birth: date
    category: Category = Category.UR
    gender: Gender = Gender.MALE
    is_pwbd: bool = False
    is_ex_serviceman: bool = False
    state: str = Field(min_length=2, max_length=64)
    district: str = Field(min_length=2, max_length=64)
    degree: str = Field(min_length=1, max_length=64)
    stream: str | None = None
    completed_year: int | None = None
    percentage: float | None = Field(default=None, ge=0, le=100)
    is_completed: bool = True


class SessionOut(BaseModel):
    email: str
    is_verified: bool
    student_id: int | None
    token: str


def _fail(problem: AuthProblem) -> HTTPException:
    return HTTPException(status_code=problem.status, detail=problem.message)


def _set_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        SESSION_COOKIE, token, httponly=True, samesite="lax", secure=False, max_age=60 * 60 * 24 * 30
    )


@router.post("/sign-up", status_code=201)
def sign_up(payload: SignUpIn, db: Session = Depends(get_db)) -> dict[str, str]:
    verdict = judge(payload.email)
    if not verdict.looks_real:
        raise HTTPException(status_code=422, detail=verdict.reason.capitalize() + ".")

    try:
        register(db, payload.email, payload.password, language=payload.language)
    except WeakPassword as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except AuthProblem as problem:
        raise _fail(problem) from problem
    return {"message": "We sent a 6 digit code to your email. It works for 10 minutes."}


@router.post("/resend-code")
def resend(payload: ResendIn, db: Session = Depends(get_db)) -> dict[str, str]:
    user = find_user(db, payload.email)
    if user is None:
        return {"message": "If that email has an account, we have sent a new code."}
    try:
        issue_code(db, user, language=payload.language)
    except AuthProblem as problem:
        raise _fail(problem) from problem
    return {"message": "If that email has an account, we have sent a new code."}


@router.post("/verify", response_model=SessionOut)
def verify(payload: CodeIn, response: Response, db: Session = Depends(get_db)) -> SessionOut:
    try:
        user = verify_code(db, payload.email, payload.code)
    except AuthProblem as problem:
        raise _fail(problem) from problem

    token = tokens.issue(user.id, user.email)
    _set_cookie(response, token)
    return SessionOut(
        email=user.email, is_verified=user.is_verified, student_id=user.student_id, token=token
    )


@router.post("/sign-in", response_model=SessionOut)
def login(payload: SignInIn, response: Response, db: Session = Depends(get_db)) -> SessionOut:
    try:
        user = sign_in(db, payload.email, payload.password)
    except AuthProblem as problem:
        raise _fail(problem) from problem

    token = tokens.issue(user.id, user.email)
    _set_cookie(response, token)
    return SessionOut(
        email=user.email, is_verified=user.is_verified, student_id=user.student_id, token=token
    )


@router.post("/sign-out")
def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(SESSION_COOKIE)
    return {"message": "Signed out."}
