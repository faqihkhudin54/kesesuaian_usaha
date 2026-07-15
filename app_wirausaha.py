from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field, field_validator

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = Path(os.getenv("MODEL_WIRAUSAHA_PATH", BASE_DIR / "model_wirausaha_pipeline.pkl"))
API_TOKEN = os.getenv("TRACER_API_TOKEN", "tracerstudy")

app = FastAPI(
    title="API Prediksi Kesesuaian Usaha Alumni",
    version="1.0.0",
)
model = joblib.load(MODEL_PATH)

DIRECT = {
    "TE": {"Servis Elektronik", "Instalasi Listrik", "Panel Kontrol", "CCTV dan Smart Home", "Toko Komponen Elektronik"},
    "PPLG": {"Web Development", "Mobile App Development", "Software House", "Game Development", "Jasa Pembuatan Sistem Informasi"},
    "TMI": {"Fabrikasi Logam", "Jasa CNC", "Bengkel Mesin Industri", "Jasa Pengelasan Industri", "Pembuatan Komponen Mesin"},
    "TSM": {"Bengkel Sepeda Motor", "Modifikasi Sepeda Motor", "Toko Sparepart Motor", "Servis Injeksi Motor", "Cuci Motor"},
    "TKR": {"Bengkel Mobil", "Body Repair Mobil", "Toko Sparepart Mobil", "Servis AC Mobil", "Cuci dan Detailing Mobil"},
}
ADJACENT = {
    "TE": {"Servis Peralatan Rumah Tangga", "Toko Alat Listrik", "Jasa Jaringan Komputer"},
    "PPLG": {"Digital Agency", "Konten Kreator", "Percetakan Digital", "Toko Komputer"},
    "TMI": {"Toko Perkakas Teknik", "Jasa Las Umum", "Supplier Sparepart Industri"},
    "TSM": {"Rental Motor", "Penjualan Motor Bekas", "Aksesori Motor"},
    "TKR": {"Rental Mobil", "Penjualan Mobil Bekas", "Aksesori Mobil"},
}
UNRELATED = {
    "Usaha Kuliner", "Toko Sembako", "Fashion dan Konveksi", "Laundry",
    "Budidaya Pertanian", "Peternakan", "Toko Kosmetik", "Kedai Kopi",
    "Event Organizer", "Jasa Fotografi",
}

KEYWORDS = {
    "TE": ("elektronik", "listrik", "panel", "cctv", "smart home", "komponen"),
    "PPLG": ("software", "web", "aplikasi", "app", "game", "sistem informasi", "program"),
    "TMI": ("mesin industri", "cnc", "fabrikasi", "las", "pengelasan", "komponen mesin"),
    "TSM": ("motor", "sepeda motor", "injeksi motor"),
    "TKR": ("mobil", "kendaraan ringan", "body repair", "ac mobil"),
}


def authorize(authorization: str | None = Header(default=None)) -> None:
    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401, detail="Token API tidak valid")


def relevance_level(jurusan: str, usaha_jenis: str) -> int:
    jurusan = jurusan.strip().upper()
    usaha = usaha_jenis.strip()
    if usaha in DIRECT.get(jurusan, set()):
        return 3
    if usaha in ADJACENT.get(jurusan, set()):
        return 2
    if usaha in UNRELATED:
        return 0

    normalized = usaha.casefold()
    if any(keyword in normalized for keyword in KEYWORDS.get(jurusan, ())):
        return 3

    # Bila usaha cocok dengan jurusan teknik lain, hubungannya dianggap tidak langsung.
    for other_major, keywords in KEYWORDS.items():
        if other_major != jurusan and any(keyword in normalized for keyword in keywords):
            return 1

    generic_technical = ("teknik", "komputer", "digital", "maintenance", "otomotif", "mesin", "elektrik")
    if any(keyword in normalized for keyword in generic_technical):
        return 1
    return 0


class WirausahaPayload(BaseModel):
    jurusan: str
    nilai_ujikom: float = Field(ge=0, le=100)
    nilai_kejuruan: float = Field(ge=0, le=100)
    tempat_pkl_relevan: int = Field(ge=0, le=1)
    ekskul_aktif: int = Field(ge=0, le=1)
    usaha_jenis: str = Field(min_length=2, max_length=150)
    usaha_lama_berjalan: int = Field(ge=0, le=600)
    pendapatan: int = Field(ge=0, le=2_000_000_000)

    @field_validator("jurusan")
    @classmethod
    def validate_major(cls, value: str) -> str:
        value = value.strip().upper()
        if value not in {"TE", "PPLG", "TMI", "TSM", "TKR"}:
            raise ValueError("Jurusan tidak dikenali")
        return value

    @field_validator("usaha_jenis")
    @classmethod
    def normalize_business(cls, value: str) -> str:
        return " ".join(value.strip().split())


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "model": MODEL_PATH.name}


@app.post("/predict-wirausaha", dependencies=[Depends(authorize)])
def predict_wirausaha(payload: WirausahaPayload) -> dict[str, Any]:
    level = relevance_level(payload.jurusan, payload.usaha_jenis)
    row = pd.DataFrame([{
        "jurusan": payload.jurusan,
        "nilai_ujikom": payload.nilai_ujikom,
        "nilai_kejuruan": payload.nilai_kejuruan,
        "tempat_pkl_relevan": payload.tempat_pkl_relevan,
        "ekskul_aktif": payload.ekskul_aktif,
        "usaha_jenis": payload.usaha_jenis,
        "tingkat_relevansi_usaha": level,
        "usaha_lama_berjalan": payload.usaha_lama_berjalan,
        "pendapatan": payload.pendapatan,
    }])

    prediction = str(model.predict(row)[0])
    probability_values = model.predict_proba(row)[0]
    class_probability = {
        str(label): float(probability)
        for label, probability in zip(model.classes_, probability_values)
    }

    probability = {
        "sangat_sesuai": class_probability.get("Sangat Sesuai", 0.0),
        "sesuai": class_probability.get("Sesuai", 0.0),
        "kurang_sesuai": class_probability.get("Kurang Sesuai", 0.0),
        "tidak_sesuai": class_probability.get("Tidak Sesuai", 0.0),
    }
    confidence = max(class_probability.values()) if class_probability else 0.0

    # Skor ekspektasi kelas, berbeda dari confidence.
    representatives = {
        "Sangat Sesuai": 92.5,
        "Sesuai": 77.5,
        "Kurang Sesuai": 60.0,
        "Tidak Sesuai": 25.0,
    }
    raw_score = sum(
        class_probability.get(label, 0.0) * score
        for label, score in representatives.items()
    )
    class_ranges = {
        "Sangat Sesuai": (85.0, 100.0),
        "Sesuai": (70.0, 84.99),
        "Kurang Sesuai": (50.0, 69.99),
        "Tidak Sesuai": (0.0, 49.99),
    }
    low, high = class_ranges[prediction]
    compatibility_score = round(max(low, min(high, raw_score)), 2)

    strengths: list[str] = []
    risks: list[str] = []
    if level >= 3:
        strengths.append("Jenis usaha berhubungan langsung dengan kompetensi jurusan.")
    elif level == 2:
        strengths.append("Jenis usaha masih berada pada bidang yang berdekatan dengan jurusan.")
    else:
        risks.append("Hubungan jenis usaha dengan kompetensi jurusan masih lemah.")
    if payload.nilai_kejuruan >= 80:
        strengths.append("Nilai kejuruan menunjukkan dasar kompetensi yang kuat.")
    if payload.tempat_pkl_relevan == 1:
        strengths.append("Pengalaman PKL relevan mendukung penerapan kompetensi.")
    if payload.usaha_lama_berjalan < 6:
        risks.append("Usaha masih sangat baru sehingga kestabilannya belum terlihat.")
    if payload.pendapatan < 1_500_000:
        risks.append("Pendapatan usaha masih rendah dan perlu penguatan model bisnis.")

    return {
        "prediction": prediction,
        "confidence": round(confidence, 6),
        "probability": probability,
        "analysis": {
            "score": compatibility_score,
            "relevance_level": level,
            "summary": f"Usaha diprediksi {prediction.lower()} dengan skor kesesuaian {compatibility_score:.2f}.",
            "strengths": strengths,
            "risks": risks,
        },
    }
