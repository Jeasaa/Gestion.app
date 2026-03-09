import streamlit as st
import pandas as pd
import sqlite3
import os
import io
from datetime import datetime, timedelta

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DB_PATH = "gestion_ventes.db"

st.set_page_config(
    page_title="Gestion des Ventes & Commissions",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STYLE CSS PERSONNALISÉ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<style>
    /* --- POLICE GLOBALE --- */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    
    /* --- SIDEBAR --- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    section[data-testid="stSidebar"] .stRadio label {
        color: #e2e8f0 !important;
        font-weight: 500;
        padding: 6px 0;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] .stMarkdown p {
        color: #f8fafc !important;
    }

    /* --- CARTES MÉTRIQUES --- */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    div[data-testid="stMetric"] label {
        color: #475569 !important;
        font-weight: 500;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* --- BOUTONS --- */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        box-shadow: 0 4px 12px rgba(37,99,235,0.3);
        transform: translateY(-1px);
    }

    /* --- FORMULAIRES --- */
    .stForm {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }

    /* --- TABLEAUX --- */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* --- TITRES --- */
    h1 {
        color: #0f172a;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    h2, h3 {
        color: #1e293b;
        font-weight: 600 !important;
    }

    /* --- TABS --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        font-weight: 500;
    }

    /* --- ALERTES --- */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 10px !important;
    }

    /* --- DIVIDER --- */
    hr {
        border-color: #e2e8f0 !important;
    }

    /* --- CARTE PROFIL --- */
    .profil-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: white;
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 24px;
    }
    .profil-card h3 { color: #f8fafc !important; margin: 0 0 12px 0; }
    .profil-card p { color: #cbd5e1; margin: 4px 0; }
    .profil-card .badge {
        display: inline-block;
        background: rgba(59,130,246,0.25);
        color: #93c5fd;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-top: 8px;
    }

    /* --- KPI MINI-CARDS --- */
    .kpi-row {
        display: flex;
        gap: 16px;
        margin: 16px 0;
    }
    .kpi-mini {
        flex: 1;
        background: #f1f5f9;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .kpi-mini .value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0f172a;
        font-family: 'JetBrains Mono', monospace;
    }
    .kpi-mini .label {
        font-size: 0.78rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BASE DE DONNÉES SQLite
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def get_connection():
    """Retourne une connexion SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Crée les tables si elles n'existent pas."""
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS acheteurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL UNIQUE,
            contact TEXT DEFAULT '',
            parrain TEXT DEFAULT 'Aucun',
            commission_parrain REAL DEFAULT 0.0,
            date_creation TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS commandes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT DEFAULT (datetime('now','localtime')),
            acheteur_id INTEGER NOT NULL,
            boutique TEXT NOT NULL,
            montant_total REAL NOT NULL,
            commission_vendeur_pct REAL NOT NULL,
            commission_vendeur_eur REAL NOT NULL,
            commission_parrain_eur REAL DEFAULT 0.0,
            notes TEXT DEFAULT '',
            statut TEXT DEFAULT 'En cours',
            FOREIGN KEY (acheteur_id) REFERENCES acheteurs(id)
        )
    """)

    conn.commit()
    conn.close()


# --- FONCTIONS CRUD ---

def ajouter_acheteur(nom, contact, parrain, commission_parrain):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO acheteurs (nom, contact, parrain, commission_parrain) VALUES (?, ?, ?, ?)",
            (nom.strip(), contact.strip(), parrain.strip() if parrain.strip() else "Aucun", commission_parrain)
        )
        conn.commit()
        return True, "OK"
    except sqlite3.IntegrityError:
        return False, "Un acheteur avec ce nom existe déjà."
    finally:
        conn.close()


def get_acheteurs():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM acheteurs ORDER BY nom", conn)
    conn.close()
    return df


def get_acheteur_par_id(acheteur_id):
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM acheteurs WHERE id = ?", conn, params=(acheteur_id,))
    conn.close()
    return df.iloc[0] if not df.empty else None


def supprimer_acheteur(acheteur_id):
    conn = get_connection()
    conn.execute("DELETE FROM commandes WHERE acheteur_id = ?", (acheteur_id,))
    conn.execute("DELETE FROM acheteurs WHERE id = ?", (acheteur_id,))
    conn.commit()
    conn.close()


def modifier_acheteur(acheteur_id, nom, contact, parrain, commission_parrain):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE acheteurs SET nom=?, contact=?, parrain=?, commission_parrain=? WHERE id=?",
            (nom.strip(), contact.strip(), parrain.strip() if parrain.strip() else "Aucun", commission_parrain, acheteur_id)
        )
        conn.commit()
        return True, "OK"
    except sqlite3.IntegrityError:
        return False, "Un acheteur avec ce nom existe déjà."
    finally:
        conn.close()


def ajouter_commande(acheteur_id, boutique, montant, commission_vendeur_pct, notes, statut):
    conn = get_connection()
    # Récupérer les infos parrain
    acheteur = pd.read_sql_query("SELECT * FROM acheteurs WHERE id = ?", conn, params=(acheteur_id,)).iloc[0]

    commission_vendeur_eur = montant * (commission_vendeur_pct / 100)
    commission_parrain_eur = 0.0
    if acheteur['parrain'] != "Aucun":
        commission_parrain_eur = commission_vendeur_eur * (acheteur['commission_parrain'] / 100)

    conn.execute(
        """INSERT INTO commandes (acheteur_id, boutique, montant_total, commission_vendeur_pct,
           commission_vendeur_eur, commission_parrain_eur, notes, statut)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (acheteur_id, boutique.strip(), montant, commission_vendeur_pct,
         commission_vendeur_eur, commission_parrain_eur, notes.strip(), statut)
    )
    conn.commit()
    conn.close()
    return commission_vendeur_eur, commission_parrain_eur


def get_commandes(acheteur_id=None):
    conn = get_connection()
    query = """
        SELECT c.id, c.date, a.nom AS acheteur, c.boutique, c.montant_total,
               c.commission_vendeur_pct, c.commission_vendeur_eur,
               a.parrain, c.commission_parrain_eur, c.notes, c.statut
        FROM commandes c
        JOIN acheteurs a ON c.acheteur_id = a.id
    """
    if acheteur_id:
        query += " WHERE c.acheteur_id = ?"
        df = pd.read_sql_query(query + " ORDER BY c.date DESC", conn, params=(acheteur_id,))
    else:
        df = pd.read_sql_query(query + " ORDER BY c.date DESC", conn)
    conn.close()
    return df


def supprimer_commande(commande_id):
    conn = get_connection()
    conn.execute("DELETE FROM commandes WHERE id = ?", (commande_id,))
    conn.commit()
    conn.close()


def modifier_statut_commande(commande_id, statut):
    conn = get_connection()
    conn.execute("UPDATE commandes SET statut = ? WHERE id = ?", (statut, commande_id))
    conn.commit()
    conn.close()


def export_dataframe(df, format_type="csv"):
    """Retourne les bytes d'un export CSV ou Excel."""
    if format_type == "csv":
        return df.to_csv(index=False).encode('utf-8-sig')
    else:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Données")
        return buffer.getvalue()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# INITIALISATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
init_db()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SIDEBAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with st.sidebar:
    st.markdown("## 💼 Menu principal")
    st.markdown("---")
    menu = st.radio(
        "Navigation",
        [
            "📊 Tableau de bord",
            "👤 Acheteurs",
            "🔍 Profil Acheteur",
            "➕ Nouvelle commande",
            "📋 Toutes les commandes",
            "💰 Commissions",
        ],
        label_visibility="collapsed"
    )
    st.markdown("---")

    # Stats rapides sidebar
    df_ach = get_acheteurs()
    df_cmd = get_commandes()
    st.markdown(f"**{len(df_ach)}** acheteurs · **{len(df_cmd)}** commandes")
    st.caption(f"Base : {DB_PATH}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE : TABLEAU DE BORD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if menu == "📊 Tableau de bord":
    st.markdown("# 📊 Tableau de bord")
    st.caption("Vue d'ensemble de votre activité commerciale")

    df_acheteurs = get_acheteurs()
    df_commandes = get_commandes()

    # --- KPI principaux ---
    nb_acheteurs = len(df_acheteurs)
    nb_commandes = len(df_commandes)

    if not df_commandes.empty:
        ca_total = df_commandes["montant_total"].sum()
        comm_vendeur = df_commandes["commission_vendeur_eur"].sum()
        comm_parrains = df_commandes["commission_parrain_eur"].sum()
        benefice_net = comm_vendeur - comm_parrains
        panier_moyen = ca_total / nb_commandes if nb_commandes > 0 else 0
    else:
        ca_total = comm_vendeur = comm_parrains = benefice_net = panier_moyen = 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Acheteurs", nb_acheteurs)
    col2.metric("Commandes", nb_commandes)
    col3.metric("CA Total", f"{ca_total:,.2f} €")
    col4.metric("Panier Moyen", f"{panier_moyen:,.2f} €")

    st.markdown("")

    col_f1, col_f2, col_f3 = st.columns(3)
    col_f1.metric("💵 Commissions Brutes", f"{comm_vendeur:,.2f} €")
    col_f2.metric("🤝 Dû aux Parrains", f"{comm_parrains:,.2f} €")
    col_f3.metric("✅ Bénéfice Net", f"{benefice_net:,.2f} €")

    if not df_commandes.empty:
        st.divider()

        # --- Graphiques ---
        tab_graph1, tab_graph2, tab_graph3 = st.tabs(["📈 Évolution CA", "🏪 Top Boutiques", "👥 Top Acheteurs"])

        with tab_graph1:
            df_chart = df_commandes.copy()
            df_chart['date'] = pd.to_datetime(df_chart['date'])
            df_chart = df_chart.set_index('date').resample('D')['montant_total'].sum().reset_index()
            df_chart.columns = ['Date', 'CA (€)']
            df_chart = df_chart[df_chart['CA (€)'] > 0]
            if not df_chart.empty:
                st.bar_chart(df_chart.set_index('Date'), y='CA (€)', color="#3b82f6")
            else:
                st.info("Pas assez de données pour afficher le graphique.")

        with tab_graph2:
            top_boutiques = df_commandes.groupby('boutique')['montant_total'].sum().sort_values(ascending=False).head(8)
            if not top_boutiques.empty:
                st.bar_chart(top_boutiques, color="#10b981")

        with tab_graph3:
            top_acheteurs = df_commandes.groupby('acheteur')['montant_total'].sum().sort_values(ascending=False).head(8)
            if not top_acheteurs.empty:
                st.bar_chart(top_acheteurs, color="#f59e0b")

        st.divider()

        # --- Dernières commandes ---
        st.markdown("### 🕐 Dernières commandes")
        cols_display = ["date", "acheteur", "boutique", "montant_total", "commission_vendeur_eur", "statut"]
        st.dataframe(
            df_commandes[cols_display].head(10).rename(columns={
                "date": "Date", "acheteur": "Acheteur", "boutique": "Boutique",
                "montant_total": "Montant (€)", "commission_vendeur_eur": "Commission (€)", "statut": "Statut"
            }),
            use_container_width=True,
            hide_index=True
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE : ACHETEURS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
elif menu == "👤 Acheteurs":
    st.markdown("# 👤 Gestion des Acheteurs")

    tab_ajouter, tab_liste = st.tabs(["➕ Ajouter un acheteur", "📋 Liste des acheteurs"])

    with tab_ajouter:
        with st.form("form_acheteur", clear_on_submit=True):
            st.markdown("#### Nouvel acheteur")
            col1, col2 = st.columns(2)
            with col1:
                nom_acheteur = st.text_input("Nom de l'acheteur *")
                contact = st.text_input("Contact (email ou téléphone)")
            with col2:
                parrain = st.text_input("Nom du parrain (vide si aucun)")
                commission_parrain = st.number_input("Commission parrain (%)", 0.0, 100.0, step=1.0)

            submitted = st.form_submit_button("✅ Ajouter l'acheteur", use_container_width=True)

            if submitted:
                if not nom_acheteur.strip():
                    st.error("Le nom de l'acheteur est obligatoire.")
                else:
                    ok, msg = ajouter_acheteur(nom_acheteur, contact, parrain, commission_parrain)
                    if ok:
                        st.success(f"Acheteur **{nom_acheteur}** ajouté avec succès !")
                        st.rerun()
                    else:
                        st.error(msg)

    with tab_liste:
        df_ach = get_acheteurs()
        if df_ach.empty:
            st.info("Aucun acheteur enregistré pour le moment.")
        else:
            # Barre de recherche
            recherche = st.text_input("🔎 Rechercher un acheteur", placeholder="Tapez un nom...")
            if recherche:
                df_ach = df_ach[df_ach['nom'].str.contains(recherche, case=False, na=False)]

            st.dataframe(
                df_ach[['nom', 'contact', 'parrain', 'commission_parrain', 'date_creation']].rename(columns={
                    'nom': 'Nom', 'contact': 'Contact', 'parrain': 'Parrain',
                    'commission_parrain': 'Commission (%)', 'date_creation': 'Inscrit le'
                }),
                use_container_width=True,
                hide_index=True
            )

            # Suppression
            st.markdown("---")
            st.markdown("#### ⚠️ Zone de danger")
            col_del1, col_del2 = st.columns([3, 1])
            with col_del1:
                acheteur_a_supprimer = st.selectbox(
                    "Sélectionner un acheteur à supprimer",
                    df_ach['nom'].tolist(),
                    key="del_acheteur"
                )
            with col_del2:
                st.markdown("")
                st.markdown("")
                if st.button("🗑️ Supprimer", key="btn_del_acheteur", type="secondary"):
                    row = df_ach[df_ach['nom'] == acheteur_a_supprimer].iloc[0]
                    supprimer_acheteur(int(row['id']))
                    st.success(f"Acheteur **{acheteur_a_supprimer}** et ses commandes supprimés.")
                    st.rerun()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE : PROFIL ACHETEUR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
elif menu == "🔍 Profil Acheteur":
    st.markdown("# 🔍 Profil Acheteur")

    df_ach = get_acheteurs()
    if df_ach.empty:
        st.warning("Aucun acheteur enregistré. Ajoutez-en d'abord dans la section Acheteurs.")
    else:
        acheteur_nom = st.selectbox("Sélectionnez un acheteur", df_ach['nom'].tolist())
        acheteur_row = df_ach[df_ach['nom'] == acheteur_nom].iloc[0]
        acheteur_id = int(acheteur_row['id'])

        # Carte profil
        parrain_txt = acheteur_row['parrain']
        commission_txt = f"{acheteur_row['commission_parrain']}%" if parrain_txt != "Aucun" else ""
        badge_parrain = f'<span class="badge">Parrain : {parrain_txt} ({commission_txt})</span>' if parrain_txt != "Aucun" else '<span class="badge">Pas de parrain</span>'

        st.markdown(f"""
        <div class="profil-card">
            <h3>👤 {acheteur_row['nom']}</h3>
            <p>📧 {acheteur_row['contact'] or 'Non renseigné'}</p>
            <p>📅 Inscrit le {acheteur_row['date_creation']}</p>
            {badge_parrain}
        </div>
        """, unsafe_allow_html=True)

        # Stats de l'acheteur
        df_hist = get_commandes(acheteur_id)

        if not df_hist.empty:
            total_achats = df_hist['montant_total'].sum()
            nb_cmd = len(df_hist)
            moy_achat = total_achats / nb_cmd

            st.markdown(f"""
            <div class="kpi-row">
                <div class="kpi-mini">
                    <div class="value">{nb_cmd}</div>
                    <div class="label">Commandes</div>
                </div>
                <div class="kpi-mini">
                    <div class="value">{total_achats:,.2f} €</div>
                    <div class="label">Total Dépensé</div>
                </div>
                <div class="kpi-mini">
                    <div class="value">{moy_achat:,.2f} €</div>
                    <div class="label">Panier Moyen</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### Historique des commandes")
            st.dataframe(
                df_hist[['date', 'boutique', 'montant_total', 'commission_vendeur_eur', 'statut', 'notes']].rename(columns={
                    'date': 'Date', 'boutique': 'Boutique', 'montant_total': 'Montant (€)',
                    'commission_vendeur_eur': 'Commission (€)', 'statut': 'Statut', 'notes': 'Notes'
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Aucun achat enregistré pour cet acheteur.")

        # Modifier l'acheteur
        st.divider()
        with st.expander("✏️ Modifier les informations"):
            with st.form("form_edit_acheteur"):
                new_nom = st.text_input("Nom", value=acheteur_row['nom'])
                new_contact = st.text_input("Contact", value=acheteur_row['contact'])
                new_parrain = st.text_input("Parrain", value=acheteur_row['parrain'] if acheteur_row['parrain'] != "Aucun" else "")
                new_comm = st.number_input("Commission parrain (%)", value=float(acheteur_row['commission_parrain']), min_value=0.0, max_value=100.0)

                if st.form_submit_button("💾 Sauvegarder les modifications"):
                    ok, msg = modifier_acheteur(acheteur_id, new_nom, new_contact, new_parrain, new_comm)
                    if ok:
                        st.success("Informations mises à jour !")
                        st.rerun()
                    else:
                        st.error(msg)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE : NOUVELLE COMMANDE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
elif menu == "➕ Nouvelle commande":
    st.markdown("# ➕ Nouvelle commande")

    df_ach = get_acheteurs()
    if df_ach.empty:
        st.warning("Ajoutez d'abord un acheteur avant de créer une commande.")
    else:
        with st.form("form_commande", clear_on_submit=True):
            # Sélection acheteur avec affichage du parrain
            acheteur_nom = st.selectbox("Acheteur", df_ach['nom'].tolist())
            acheteur_row = df_ach[df_ach['nom'] == acheteur_nom].iloc[0]

            if acheteur_row['parrain'] != "Aucun":
                st.info(f"🤝 Parrain : **{acheteur_row['parrain']}** — Commission : **{acheteur_row['commission_parrain']}%**")

            boutique = st.text_input("Boutique / Site web *")

            col1, col2 = st.columns(2)
            with col1:
                montant = st.number_input("Montant total (€)", min_value=0.0, step=0.5)
            with col2:
                commission_pct = st.number_input("Votre commission (%)", min_value=0.0, max_value=100.0, step=1.0)

            col3, col4 = st.columns(2)
            with col3:
                statut = st.selectbox("Statut", ["En cours", "Validée", "Livrée", "Annulée"])
            with col4:
                notes = st.text_input("Notes")

            # Aperçu en temps réel
            if montant > 0 and commission_pct > 0:
                comm_v = montant * (commission_pct / 100)
                comm_p = 0.0
                if acheteur_row['parrain'] != "Aucun":
                    comm_p = comm_v * (acheteur_row['commission_parrain'] / 100)
                st.caption(f"📊 Aperçu — Commission vendeur : **{comm_v:.2f} €** | Parrain : **{comm_p:.2f} €** | Net : **{comm_v - comm_p:.2f} €**")

            submitted = st.form_submit_button("✅ Enregistrer la commande", use_container_width=True)

            if submitted:
                if not boutique.strip():
                    st.error("Le nom de la boutique est obligatoire.")
                elif montant <= 0:
                    st.error("Le montant doit être supérieur à 0.")
                else:
                    comm_v, comm_p = ajouter_commande(
                        int(acheteur_row['id']), boutique, montant, commission_pct, notes, statut
                    )
                    st.success(f"Commande enregistrée ! Commission : **{comm_v:.2f} €** | Parrain : **{comm_p:.2f} €**")
                    st.rerun()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE : TOUTES LES COMMANDES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
elif menu == "📋 Toutes les commandes":
    st.markdown("# 📋 Toutes les commandes")

    df_commandes = get_commandes()

    if df_commandes.empty:
        st.info("Aucune commande enregistrée pour le moment.")
    else:
        # --- FILTRES ---
        st.markdown("#### 🔎 Filtres")
        col_f1, col_f2, col_f3 = st.columns(3)

        with col_f1:
            filtre_acheteur = st.multiselect("Acheteur", df_commandes['acheteur'].unique().tolist())
        with col_f2:
            filtre_boutique = st.multiselect("Boutique", df_commandes['boutique'].unique().tolist())
        with col_f3:
            filtre_statut = st.multiselect("Statut", df_commandes['statut'].unique().tolist())

        # Filtre date
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            date_debut = st.date_input("Du", value=None)
        with col_d2:
            date_fin = st.date_input("Au", value=None)

        # Appliquer les filtres
        df_filtered = df_commandes.copy()
        if filtre_acheteur:
            df_filtered = df_filtered[df_filtered['acheteur'].isin(filtre_acheteur)]
        if filtre_boutique:
            df_filtered = df_filtered[df_filtered['boutique'].isin(filtre_boutique)]
        if filtre_statut:
            df_filtered = df_filtered[df_filtered['statut'].isin(filtre_statut)]
        if date_debut:
            df_filtered = df_filtered[pd.to_datetime(df_filtered['date']).dt.date >= date_debut]
        if date_fin:
            df_filtered = df_filtered[pd.to_datetime(df_filtered['date']).dt.date <= date_fin]

        st.markdown(f"**{len(df_filtered)}** commande(s) trouvée(s)")

        # Résumé des résultats filtrés
        if not df_filtered.empty:
            col_s1, col_s2, col_s3 = st.columns(3)
            col_s1.metric("CA filtré", f"{df_filtered['montant_total'].sum():,.2f} €")
            col_s2.metric("Commissions", f"{df_filtered['commission_vendeur_eur'].sum():,.2f} €")
            col_s3.metric("Net", f"{df_filtered['commission_vendeur_eur'].sum() - df_filtered['commission_parrain_eur'].sum():,.2f} €")

        st.divider()

        # Tableau
        display_cols = ['id', 'date', 'acheteur', 'boutique', 'montant_total',
                        'commission_vendeur_eur', 'parrain', 'commission_parrain_eur', 'statut', 'notes']
        rename_map = {
            'id': 'ID', 'date': 'Date', 'acheteur': 'Acheteur', 'boutique': 'Boutique',
            'montant_total': 'Montant (€)', 'commission_vendeur_eur': 'Commission (€)',
            'parrain': 'Parrain', 'commission_parrain_eur': 'Comm. Parrain (€)',
            'statut': 'Statut', 'notes': 'Notes'
        }
        st.dataframe(
            df_filtered[display_cols].rename(columns=rename_map),
            use_container_width=True,
            hide_index=True
        )

        # --- EXPORT ---
        st.divider()
        st.markdown("#### 📥 Exporter les données")
        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            csv_data = export_dataframe(df_filtered[display_cols].rename(columns=rename_map), "csv")
            st.download_button("📄 Exporter en CSV", csv_data, "commandes.csv", "text/csv", use_container_width=True)
        with col_ex2:
            xlsx_data = export_dataframe(df_filtered[display_cols].rename(columns=rename_map), "xlsx")
            st.download_button("📊 Exporter en Excel", xlsx_data, "commandes.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

        # --- MODIFIER STATUT / SUPPRIMER ---
        st.divider()
        st.markdown("#### ⚙️ Actions rapides")
        col_a1, col_a2, col_a3 = st.columns([2, 2, 1])
        with col_a1:
            cmd_id = st.number_input("ID de la commande", min_value=1, step=1, key="action_cmd_id")
        with col_a2:
            new_statut = st.selectbox("Nouveau statut", ["En cours", "Validée", "Livrée", "Annulée"], key="action_statut")
        with col_a3:
            st.markdown("")
            st.markdown("")
            if st.button("✏️ Modifier", key="btn_modif_statut"):
                if cmd_id in df_commandes['id'].values:
                    modifier_statut_commande(int(cmd_id), new_statut)
                    st.success(f"Commande #{cmd_id} → **{new_statut}**")
                    st.rerun()
                else:
                    st.error("ID introuvable.")

        col_d1, col_d2 = st.columns([3, 1])
        with col_d1:
            cmd_del_id = st.number_input("ID commande à supprimer", min_value=1, step=1, key="del_cmd_id")
        with col_d2:
            st.markdown("")
            st.markdown("")
            if st.button("🗑️ Supprimer", key="btn_del_cmd", type="secondary"):
                if cmd_del_id in df_commandes['id'].values:
                    supprimer_commande(int(cmd_del_id))
                    st.success(f"Commande #{cmd_del_id} supprimée.")
                    st.rerun()
                else:
                    st.error("ID introuvable.")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE : COMMISSIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
elif menu == "💰 Commissions":
    st.markdown("# 💰 Récapitulatif des Commissions")

    df_commandes = get_commandes()

    if df_commandes.empty:
        st.info("Aucune commande enregistrée.")
    else:
        tab1, tab2 = st.tabs(["🤝 Commissions Parrains", "📊 Détail Vendeur"])

        with tab1:
            df_parrains = df_commandes[df_commandes['parrain'] != "Aucun"]
            if df_parrains.empty:
                st.info("Aucune commission de parrainage pour le moment.")
            else:
                recap = df_parrains.groupby('parrain').agg(
                    Nb_Filleuls_Actifs=('acheteur', 'nunique'),
                    Nb_Commandes=('id', 'count'),
                    CA_Filleuls=('montant_total', 'sum'),
                    Total_Commissions=('commission_parrain_eur', 'sum')
                ).reset_index().rename(columns={'parrain': 'Parrain'})

                recap = recap.sort_values('Total_Commissions', ascending=False)

                # KPI
                total_du = recap['Total_Commissions'].sum()
                st.metric("Total dû aux parrains", f"{total_du:,.2f} €")

                st.dataframe(recap, use_container_width=True, hide_index=True)

                # Graphique
                st.bar_chart(recap.set_index('Parrain')['Total_Commissions'], color="#8b5cf6")

                # Export
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button("📄 CSV", export_dataframe(recap, "csv"),
                                       "commissions_parrains.csv", "text/csv", use_container_width=True)
                with col2:
                    st.download_button("📊 Excel", export_dataframe(recap, "xlsx"),
                                       "commissions_parrains.xlsx",
                                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                       use_container_width=True)

        with tab2:
            st.markdown("### Récapitulatif par boutique")
            recap_boutique = df_commandes.groupby('boutique').agg(
                Nb_Commandes=('id', 'count'),
                CA=('montant_total', 'sum'),
                Commission_Vendeur=('commission_vendeur_eur', 'sum'),
                Commission_Parrain=('commission_parrain_eur', 'sum')
            ).reset_index()
            recap_boutique['Net'] = recap_boutique['Commission_Vendeur'] - recap_boutique['Commission_Parrain']
            recap_boutique = recap_boutique.sort_values('Net', ascending=False)
            recap_boutique = recap_boutique.rename(columns={'boutique': 'Boutique'})

            st.dataframe(recap_boutique, use_container_width=True, hide_index=True)
            st.bar_chart(recap_boutique.set_index('Boutique')['Net'], color="#10b981")
