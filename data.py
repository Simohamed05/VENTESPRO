import base64
import traceback
from typing import Optional

import pandas as pd
import streamlit as st


@st.cache_data(ttl=3600)
def load_data(file) -> Optional[pd.DataFrame]:
    """Charge et prépare les données (CSV / Excel / TXT / Parquet)."""
    try:
        file_extension = (file.name.split('.')[-1] if hasattr(file, "name") else "").lower()
        df = None

        def _read_csv_like(f):
            separators = [';', ',', '\t', '|']
            encodings = ['utf-8', 'latin-1']
            for sep in separators:
                for enc in encodings:
                    try:
                        f.seek(0)
                        _df = pd.read_csv(f, sep=sep, encoding=enc)
                        if _df is not None and len(_df.columns) > 1:
                            return _df
                    except Exception:
                        continue
            try:
                f.seek(0)
                _df = pd.read_csv(f, sep=None, engine="python")
                if _df is not None and len(_df.columns) > 1:
                    return _df
            except Exception:
                return None
            return None

        if file_extension in ['csv', 'txt', 'tsv']:
            df = _read_csv_like(file)
        elif file_extension in ['xlsx', 'xls']:
            file.seek(0)
            df = pd.read_excel(file)
        elif file_extension in ['parquet']:
            try:
                file.seek(0)
                df = pd.read_parquet(file)
            except Exception as exc:
                st.error(
                    "❌ Lecture Parquet impossible (pyarrow/fastparquet requis). "
                    f"Détail: {str(exc)}"
                )
                st.code(traceback.format_exc())
                return None
        else:
            df = _read_csv_like(file)
            if df is None:
                st.error("❌ Format de fichier non supporté. Utilisez CSV, Excel, TXT/TSV ou Parquet.")
                return None

        if df is None or len(df.columns) <= 1:
            st.error("❌ Impossible de lire le fichier ou fichier vide.")
            return None

        df.columns = [str(c).strip() for c in df.columns]
        return df

    except Exception as exc:
        st.error(f"❌ Erreur lors du chargement du fichier: {str(exc)}")
        return None


def create_download_link(df: pd.DataFrame, filename: str) -> str:
    """Crée un lien de téléchargement pour un DataFrame."""
    csv = df.to_csv(index=False).encode('utf-8')
    b64 = base64.b64encode(csv).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}" class="download-link">📥 Télécharger {filename}</a>'
