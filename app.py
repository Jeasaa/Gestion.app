import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import io
import json
from datetime import datetime, timedelta

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONFIG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DB_PATH = "gestion_ventes.db"
TECHNIQUES = ["FTID", "LIT", "RTS", "DNA", "EB"]
CATEGORIES_COUTS = ["FTID", "LIT", "RTS"]

st.set_page_config(page_title="SalesFlow", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

for k, v in [('authenticated', False), ('username', ''), ('dark_mode', False),
             ('show_new_order', False), ('show_new_order_page', False)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CSS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def inject_css(dark=False):
    if dark:
        bg="#0b1120";bg2="#111827";bg3="#1f2937";text="#f9fafb";text2="#d1d5db";text3="#9ca3af"
        accent="#6366f1";accent2="#4f46e5";accent_glow="rgba(99,102,241,0.35)"
        card_border="#374151";metric_bg="linear-gradient(135deg,#111827,#1f2937)"
        sidebar_bg="linear-gradient(195deg,#0b1120 0%,#1e1b4b 100%)"
        form_bg="#111827";form_border="#374151";kpi_bg="#1f2937"
        input_bg="#1f2937";input_border="#374151";input_text="#f9fafb"
        profil_bg="linear-gradient(135deg,#1e1b4b,#312e81)"
        badge_bg="rgba(99,102,241,0.2)";badge_text="#a5b4fc"
    else:
        bg="#f8fafc";bg2="#ffffff";bg3="#f1f5f9";text="#0f172a";text2="#334155";text3="#64748b"
        accent="#6366f1";accent2="#4f46e5";accent_glow="rgba(99,102,241,0.25)"
        card_border="#e2e8f0";metric_bg="linear-gradient(135deg,#ffffff,#f1f5f9)"
        sidebar_bg="linear-gradient(195deg,#0f172a 0%,#1e1b4b 100%)"
        form_bg="#ffffff";form_border="#e2e8f0";kpi_bg="#f1f5f9"
        input_bg="#ffffff";input_border="#cbd5e1";input_text="#0f172a"
        profil_bg="linear-gradient(135deg,#1e1b4b,#312e81)"
        badge_bg="rgba(99,102,241,0.1)";badge_text="#6366f1"

    st.markdown(f"""<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    html,body,[class*="css"]{{font-family:'Outfit',sans-serif;}}
    .stApp{{background:{bg};}}
    section[data-testid="stSidebar"]{{background:{sidebar_bg};}}
    section[data-testid="stSidebar"] *{{color:#e2e8f0 !important;}}
    section[data-testid="stSidebar"] .stRadio label{{font-weight:500;padding:8px 4px;border-radius:8px;transition:all .15s;}}
    div[data-testid="stMetric"]{{background:{metric_bg};border:1px solid {card_border};border-radius:16px;padding:20px 24px;box-shadow:0 1px 3px rgba(0,0,0,0.05);transition:transform .15s;}}
    div[data-testid="stMetric"]:hover{{transform:translateY(-2px);}}
    div[data-testid="stMetric"] label{{color:{text3} !important;font-weight:600;font-size:0.8rem !important;text-transform:uppercase;letter-spacing:0.8px;}}
    div[data-testid="stMetric"] [data-testid="stMetricValue"]{{color:{text} !important;font-weight:700;font-family:'JetBrains Mono',monospace !important;}}
    .stButton>button{{background:linear-gradient(135deg,{accent},{accent2});color:white;border:none;border-radius:10px;font-weight:600;padding:0.55rem 1.6rem;transition:all .2s;}}
    .stButton>button:hover{{box-shadow:0 4px 16px {accent_glow};transform:translateY(-1px);}}
    .stForm{{background:{form_bg};border:1px solid {form_border};border-radius:16px;padding:28px;}}
    .stTextInput input,.stNumberInput input,.stTextArea textarea{{background:{input_bg} !important;color:{input_text} !important;border-color:{input_border} !important;border-radius:10px !important;}}
    .stSelectbox>div>div{{background:{input_bg} !important;color:{input_text} !important;border-color:{input_border} !important;border-radius:10px !important;}}
    .stDataFrame{{border-radius:12px;overflow:hidden;}}
    h1{{color:{text};font-weight:800 !important;}}
    h2,h3{{color:{text2};font-weight:700 !important;}}
    p,li,span,label,.stMarkdown{{color:{text2};}}
    .stTabs [data-baseweb="tab-list"]{{gap:4px;}}
    .stTabs [data-baseweb="tab"]{{border-radius:10px 10px 0 0;font-weight:600;}}
    .stSuccess,.stInfo,.stWarning,.stError{{border-radius:12px !important;}}
    hr{{border-color:{card_border} !important;}}
    .profil-card{{background:{profil_bg};color:white;border-radius:20px;padding:32px;margin-bottom:24px;box-shadow:0 4px 24px rgba(99,102,241,0.15);}}
    .profil-card h3{{color:#f8fafc !important;margin:0 0 16px 0;font-size:1.5rem;}}
    .profil-card p{{color:#c7d2fe;margin:4px 0;}}
    .profil-card .badge{{display:inline-block;background:{badge_bg};color:{badge_text};padding:5px 14px;border-radius:20px;font-size:0.82rem;font-weight:600;margin-top:10px;}}
    .kpi-row{{display:flex;gap:16px;margin:16px 0;}}
    .kpi-mini{{flex:1;background:{kpi_bg};border:1px solid {card_border};border-radius:14px;padding:18px;text-align:center;transition:transform .15s;}}
    .kpi-mini:hover{{transform:translateY(-2px);}}
    .kpi-mini .value{{font-size:1.6rem;font-weight:700;color:{text};font-family:'JetBrains Mono',monospace;}}
    .kpi-mini .label{{font-size:0.75rem;color:{text3};text-transform:uppercase;letter-spacing:0.8px;margin-top:6px;font-weight:600;}}
    .obj-bar-bg{{background:{kpi_bg};border:1px solid {card_border};border-radius:12px;height:36px;overflow:hidden;margin:8px 0;}}
    .obj-bar-fill{{height:100%;border-radius:12px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:0.85rem;color:white;font-family:'JetBrains Mono',monospace;transition:width .6s cubic-bezier(0.4,0,0.2,1);}}
    .note-bubble{{background:{kpi_bg};border-left:4px solid {accent};border-radius:0 14px 14px 0;padding:14px 18px;margin:10px 0;color:{text2};}}
    .note-bubble .note-date{{font-size:0.75rem;color:{text3};margin-bottom:6px;font-weight:500;}}
    .cred-box{{background:{kpi_bg};border:1px solid {card_border};border-radius:14px;padding:18px;margin:8px 0;font-family:'JetBrains Mono',monospace;font-size:0.88rem;color:{text2};white-space:pre-wrap;}}
    .pending-card{{background:{kpi_bg};border:1px solid {card_border};border-radius:16px;padding:24px;margin:16px 0;}}
    .pending-card h4{{color:{text};margin:0 0 12px 0;}}
    .cost-row{{display:flex;gap:12px;align-items:center;padding:6px 12px;background:{bg3};border-radius:8px;margin:4px 0;font-size:0.9rem;}}
    .cost-cat{{font-weight:600;color:{accent};min-width:60px;}}
    .cost-val{{color:{text};font-family:'JetBrains Mono',monospace;}}
    .tech-badge{{display:inline-block;background:{badge_bg};color:{badge_text};padding:3px 10px;border-radius:8px;font-size:0.78rem;font-weight:600;margin:2px 4px 2px 0;}}
    </style>""", unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATABASE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def get_conn():
    conn = sqlite3.connect(DB_PATH); conn.execute("PRAGMA journal_mode=WAL"); conn.execute("PRAGMA foreign_keys=ON"); return conn

def init_db():
    conn = get_conn(); c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL, role TEXT DEFAULT 'admin',
        created_at TEXT DEFAULT (datetime('now','localtime')))""")
    if c.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        c.execute("INSERT INTO users (username,password_hash,role) VALUES (?,?,?)",
                  ("admin", hashlib.sha256("admin".encode()).hexdigest(), "admin"))
    c.execute("""CREATE TABLE IF NOT EXISTS acheteurs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT NOT NULL UNIQUE,
        contact TEXT DEFAULT '', email TEXT DEFAULT '', adresse TEXT DEFAULT '',
        parrain TEXT DEFAULT 'Aucun', commission_parrain REAL DEFAULT 0.0,
        identifiants_boutique TEXT DEFAULT '',
        date_creation TEXT DEFAULT (datetime('now','localtime')))""")
    c.execute("""CREATE TABLE IF NOT EXISTS commandes (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT DEFAULT (datetime('now','localtime')),
        acheteur_id INTEGER NOT NULL, boutique TEXT NOT NULL,
        montant_total REAL NOT NULL, commission_mode TEXT DEFAULT 'pct',
        commission_vendeur_pct REAL DEFAULT 0.0, commission_vendeur_eur REAL NOT NULL,
        commission_parrain_eur REAL DEFAULT 0.0, notes TEXT DEFAULT '',
        statut TEXT DEFAULT 'En cours',
        technique TEXT DEFAULT '',
        couts_details TEXT DEFAULT '{}',
        cout_total REAL DEFAULT 0.0,
        est_recurrente INTEGER DEFAULT 0, frequence_jours INTEGER DEFAULT 0,
        prochaine_date TEXT DEFAULT '',
        FOREIGN KEY (acheteur_id) REFERENCES acheteurs(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS notes_acheteurs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, acheteur_id INTEGER NOT NULL,
        contenu TEXT NOT NULL, date_creation TEXT DEFAULT (datetime('now','localtime')),
        auteur TEXT DEFAULT 'admin', FOREIGN KEY (acheteur_id) REFERENCES acheteurs(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS objectifs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, mois TEXT NOT NULL UNIQUE,
        objectif_ca REAL DEFAULT 0.0, objectif_commandes INTEGER DEFAULT 0)""")
    c.execute("""CREATE TABLE IF NOT EXISTS demandes (
        id INTEGER PRIMARY KEY AUTOINCREMENT, date_soumission TEXT DEFAULT (datetime('now','localtime')),
        nom_client TEXT NOT NULL, telephone TEXT DEFAULT '', email TEXT DEFAULT '',
        boutique TEXT NOT NULL, montant REAL NOT NULL, identifiants TEXT DEFAULT '',
        notes_client TEXT DEFAULT '', statut TEXT DEFAULT 'En attente')""")
    conn.commit(); conn.close()

# ━━━ AUTH ━━━
def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()
def auth_check(u,p):
    conn=get_conn(); r=conn.execute("SELECT * FROM users WHERE username=? AND password_hash=?",(u,hash_pw(p))).fetchone(); conn.close(); return r is not None
def change_pw(u,np):
    conn=get_conn(); conn.execute("UPDATE users SET password_hash=? WHERE username=?",(hash_pw(np),u)); conn.commit(); conn.close()

# ━━━ ACHETEURS ━━━
def get_or_create_acheteur(nom, contact="", email="", identifiants=""):
    conn=get_conn()
    row=conn.execute("SELECT id FROM acheteurs WHERE nom=?",(nom.strip(),)).fetchone()
    if row: aid=row[0]
    else:
        c=conn.execute("INSERT INTO acheteurs (nom,contact,email,identifiants_boutique) VALUES (?,?,?,?)",
                       (nom.strip(),contact.strip(),email.strip(),identifiants.strip()))
        aid=c.lastrowid; conn.commit()
    conn.close(); return aid

def ajouter_acheteur(nom,contact,parrain,comm_p,email="",adresse="",identifiants=""):
    conn=get_conn()
    try:
        conn.execute("INSERT INTO acheteurs (nom,contact,email,adresse,parrain,commission_parrain,identifiants_boutique) VALUES (?,?,?,?,?,?,?)",
            (nom.strip(),contact.strip(),email.strip(),adresse.strip(),parrain.strip() if parrain.strip() else "Aucun",comm_p,identifiants.strip()))
        conn.commit(); return True,"OK"
    except sqlite3.IntegrityError: return False,"Ce nom existe déjà."
    finally: conn.close()

def get_acheteurs():
    conn=get_conn(); df=pd.read_sql_query("SELECT * FROM acheteurs ORDER BY nom",conn); conn.close(); return df

def supprimer_acheteur(aid):
    conn=get_conn()
    for t in ["notes_acheteurs","commandes"]: conn.execute(f"DELETE FROM {t} WHERE acheteur_id=?",(aid,))
    conn.execute("DELETE FROM acheteurs WHERE id=?",(aid,)); conn.commit(); conn.close()

def modifier_acheteur(aid,nom,contact,email,adresse,parrain,comm_p,identifiants):
    conn=get_conn()
    try:
        conn.execute("UPDATE acheteurs SET nom=?,contact=?,email=?,adresse=?,parrain=?,commission_parrain=?,identifiants_boutique=? WHERE id=?",
            (nom.strip(),contact.strip(),email.strip(),adresse.strip(),parrain.strip() if parrain.strip() else "Aucun",comm_p,identifiants.strip(),aid))
        conn.commit(); return True,"OK"
    except sqlite3.IntegrityError: return False,"Ce nom existe déjà."
    finally: conn.close()

# ━━━ COMMANDES ━━━
def calc_comm(montant,mode,pct_val,eur_val,parrain,comm_parrain_pct):
    if mode=="pct": cv=montant*(pct_val/100); pf=pct_val
    else: cv=eur_val; pf=(eur_val/montant*100) if montant>0 else 0
    cp=cv*(comm_parrain_pct/100) if parrain!="Aucun" and comm_parrain_pct>0 else 0.0
    return cv,cp,pf

def ajouter_commande(acheteur_nom,boutique,montant,comm_mode,comm_pct,comm_eur,
                     notes,statut,technique,couts_details,
                     est_rec=False,freq_j=0,contact="",email="",identifiants=""):
    aid=get_or_create_acheteur(acheteur_nom,contact,email,identifiants)
    conn=get_conn()
    ach=pd.read_sql_query("SELECT * FROM acheteurs WHERE id=?",conn,params=(aid,)).iloc[0]
    cv,cp,pf=calc_comm(montant,comm_mode,comm_pct,comm_eur,ach['parrain'],ach['commission_parrain'])
    cout_total=sum(couts_details.values())
    prochaine=""
    if est_rec and freq_j>0: prochaine=(datetime.now()+timedelta(days=freq_j)).strftime("%Y-%m-%d")
    conn.execute("""INSERT INTO commandes (acheteur_id,boutique,montant_total,commission_mode,
        commission_vendeur_pct,commission_vendeur_eur,commission_parrain_eur,notes,statut,
        technique,couts_details,cout_total,est_recurrente,frequence_jours,prochaine_date)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (aid,boutique.strip(),montant,comm_mode,pf,cv,cp,notes.strip(),statut,
         technique,json.dumps(couts_details),cout_total,1 if est_rec else 0,freq_j,prochaine))
    conn.commit(); conn.close(); return cv,cp,cout_total

def modifier_commande(cid,boutique,montant,comm_mode,comm_pct,comm_eur,notes,statut,technique,couts_details):
    conn=get_conn()
    row=conn.execute("SELECT acheteur_id FROM commandes WHERE id=?",(cid,)).fetchone()
    if not row: conn.close(); return
    ach=pd.read_sql_query("SELECT * FROM acheteurs WHERE id=?",conn,params=(row[0],)).iloc[0]
    cv,cp,pf=calc_comm(montant,comm_mode,comm_pct,comm_eur,ach['parrain'],ach['commission_parrain'])
    cout_total=sum(couts_details.values())
    conn.execute("""UPDATE commandes SET boutique=?,montant_total=?,commission_mode=?,
        commission_vendeur_pct=?,commission_vendeur_eur=?,commission_parrain_eur=?,notes=?,statut=?,
        technique=?,couts_details=?,cout_total=? WHERE id=?""",
        (boutique.strip(),montant,comm_mode,pf,cv,cp,notes.strip(),statut,
         technique,json.dumps(couts_details),cout_total,cid))
    conn.commit(); conn.close()

def get_commandes(acheteur_id=None):
    conn=get_conn()
    q="""SELECT c.id,c.date,a.nom AS acheteur,c.boutique,c.montant_total,
        c.commission_mode,c.commission_vendeur_pct,c.commission_vendeur_eur,
        a.parrain,c.commission_parrain_eur,c.notes,c.statut,
        c.technique,c.couts_details,c.cout_total,
        c.est_recurrente,c.frequence_jours,c.prochaine_date,c.acheteur_id
        FROM commandes c JOIN acheteurs a ON c.acheteur_id=a.id"""
    if acheteur_id: q+=" WHERE c.acheteur_id=?"; df=pd.read_sql_query(q+" ORDER BY c.date DESC",conn,params=(acheteur_id,))
    else: df=pd.read_sql_query(q+" ORDER BY c.date DESC",conn)
    conn.close(); return df

def supprimer_commande(cid):
    conn=get_conn(); conn.execute("DELETE FROM commandes WHERE id=?",(cid,)); conn.commit(); conn.close()

# ━━━ DEMANDES ━━━
def get_demandes(statut=None):
    conn=get_conn()
    if statut: df=pd.read_sql_query("SELECT * FROM demandes WHERE statut=? ORDER BY date_soumission DESC",conn,params=(statut,))
    else: df=pd.read_sql_query("SELECT * FROM demandes ORDER BY date_soumission DESC",conn)
    conn.close(); return df
def valider_demande(did):
    conn=get_conn(); conn.execute("UPDATE demandes SET statut='Validée' WHERE id=?",(did,)); conn.commit(); conn.close()
def rejeter_demande(did):
    conn=get_conn(); conn.execute("UPDATE demandes SET statut='Rejetée' WHERE id=?",(did,)); conn.commit(); conn.close()
def count_pending():
    conn=get_conn(); n=conn.execute("SELECT COUNT(*) FROM demandes WHERE statut='En attente'").fetchone()[0]; conn.close(); return n

# ━━━ NOTES / OBJECTIFS / ETC ━━━
def ajouter_note(aid,contenu,auteur="admin"):
    conn=get_conn(); conn.execute("INSERT INTO notes_acheteurs (acheteur_id,contenu,auteur) VALUES (?,?,?)",(aid,contenu.strip(),auteur)); conn.commit(); conn.close()
def get_notes(aid):
    conn=get_conn(); df=pd.read_sql_query("SELECT * FROM notes_acheteurs WHERE acheteur_id=? ORDER BY date_creation DESC",conn,params=(aid,)); conn.close(); return df
def supprimer_note(nid):
    conn=get_conn(); conn.execute("DELETE FROM notes_acheteurs WHERE id=?",(nid,)); conn.commit(); conn.close()
def get_objectif_mois(m):
    conn=get_conn(); r=conn.execute("SELECT * FROM objectifs WHERE mois=?",(m,)).fetchone(); conn.close()
    return {"id":r[0],"mois":r[1],"objectif_ca":r[2],"objectif_commandes":r[3]} if r else None
def set_objectif_mois(m,oca,ocmd):
    conn=get_conn()
    if conn.execute("SELECT id FROM objectifs WHERE mois=?",(m,)).fetchone():
        conn.execute("UPDATE objectifs SET objectif_ca=?,objectif_commandes=? WHERE mois=?",(oca,ocmd,m))
    else: conn.execute("INSERT INTO objectifs (mois,objectif_ca,objectif_commandes) VALUES (?,?,?)",(m,oca,ocmd))
    conn.commit(); conn.close()
def traiter_recurrences():
    conn=get_conn(); today=datetime.now().strftime("%Y-%m-%d")
    rows=conn.execute("SELECT * FROM commandes WHERE est_recurrente=1 AND prochaine_date<=? AND statut!='Annulée'",(today,)).fetchall()
    count=0
    for r in rows:
        cid,aid,bout,mont=r[0],r[2],r[3],r[4]; cpct,ceur,cparr=r[6],r[7],r[8]; notes=r[9]; freq,proch=r[15],r[16]
        conn.execute("INSERT INTO commandes (acheteur_id,boutique,montant_total,commission_mode,commission_vendeur_pct,commission_vendeur_eur,commission_parrain_eur,notes,statut,technique,couts_details,cout_total) VALUES (?,?,?,'pct',?,?,?,?,'En cours',?,?,?)",
            (aid,bout,mont,cpct,ceur,cparr,f"[Auto] {notes}",r[12],r[13],r[14])); 
        nd=(datetime.strptime(proch,"%Y-%m-%d")+timedelta(days=freq)).strftime("%Y-%m-%d")
        conn.execute("UPDATE commandes SET prochaine_date=? WHERE id=?",(nd,cid)); count+=1
    conn.commit(); conn.close(); return count
def recherche_globale(terme):
    conn=get_conn(); t=f"%{terme}%"
    a=pd.read_sql_query("SELECT 'Acheteur' as type,id,nom as titre,contact as detail FROM acheteurs WHERE nom LIKE ? OR contact LIKE ?",conn,params=(t,t))
    c=pd.read_sql_query("SELECT 'Commande' as type,c.id,c.boutique as titre,a.nom||' — '||c.montant_total||'€' as detail FROM commandes c JOIN acheteurs a ON c.acheteur_id=a.id WHERE c.boutique LIKE ? OR a.nom LIKE ? OR c.notes LIKE ?",conn,params=(t,t,t))
    n=pd.read_sql_query("SELECT 'Note' as type,n.id,n.contenu as titre,a.nom as detail FROM notes_acheteurs n JOIN acheteurs a ON n.acheteur_id=a.id WHERE n.contenu LIKE ?",conn,params=(t,))
    conn.close(); return pd.concat([a,c,n],ignore_index=True)
def export_df(df,fmt="csv"):
    if fmt=="csv": return df.to_csv(index=False).encode('utf-8-sig')
    buf=io.BytesIO()
    with pd.ExcelWriter(buf,engine='openpyxl') as w: df.to_excel(w,index=False,sheet_name="Données")
    return buf.getvalue()
def get_finance_summary(df):
    if df.empty: return 0,0
    av=df[df['statut'].isin(['En cours','Livrée'])]['commission_vendeur_eur'].sum()
    rc=df[df['statut']=='Validée']['commission_vendeur_eur'].sum()
    return av,rc

# ━━━ HELPERS UI ━━━
def render_couts_form(prefix, existing=None):
    """Affiche les champs de coûts détaillés. Retourne dict {catégorie: montant}."""
    couts = {}
    st.markdown("**💰 Coûts détaillés**")
    for cat in CATEGORIES_COUTS:
        default_val = existing.get(cat, 0.0) if existing else 0.0
        val = st.number_input(f"Coût {cat} (€)", min_value=0.0, step=0.5, value=float(default_val), key=f"{prefix}_cout_{cat}")
        if val > 0:
            couts[cat] = val
    total = sum(couts.values())
    if total > 0:
        st.caption(f"**Coût total : {total:.2f} €**")
    return couts

def render_couts_display(couts_json, cout_total):
    """Affiche les coûts d'une commande."""
    try:
        couts = json.loads(couts_json) if isinstance(couts_json, str) else couts_json
    except: couts = {}
    if couts:
        for cat, val in couts.items():
            st.markdown(f'<div class="cost-row"><span class="cost-cat">{cat}</span><span class="cost-val">{val:.2f} €</span></div>', unsafe_allow_html=True)
    st.markdown(f"**Total coûts : {cout_total:.2f} €**")

def render_technique_badges(technique_str):
    if not technique_str: return ""
    techs = [t.strip() for t in technique_str.split(",") if t.strip()]
    return "".join([f'<span class="tech-badge">{t}</span>' for t in techs])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# INIT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
init_db()
if 'rec_done' not in st.session_state:
    nb=traiter_recurrences(); st.session_state['rec_done']=True
    if nb>0: st.toast(f"🔄 {nb} récurrence(s) générée(s)")
inject_css(st.session_state['dark_mode'])

# ━━━ LOGIN ━━━
if not st.session_state['authenticated']:
    st.markdown(""); st.markdown("")
    _,cc,_=st.columns([1,2,1])
    with cc:
        st.markdown("# ⚡ SalesFlow"); st.caption("Gestion des Ventes & Commissions"); st.markdown("")
        with st.form("login"):
            u=st.text_input("Identifiant"); p=st.text_input("Mot de passe",type="password")
            if st.form_submit_button("Se connecter",use_container_width=True):
                if auth_check(u,p): st.session_state['authenticated']=True; st.session_state['username']=u; st.rerun()
                else: st.error("Identifiants incorrects.")
        st.caption("Par défaut : `admin` / `admin`")
    st.stop()

# ━━━ SIDEBAR ━━━
nb_pend=count_pending()
with st.sidebar:
    st.markdown("### ⚡ SalesFlow"); st.caption(f"Connecté : {st.session_state['username']}"); st.markdown("---")
    dark=st.toggle("🌙 Mode sombre",value=st.session_state['dark_mode'])
    if dark!=st.session_state['dark_mode']: st.session_state['dark_mode']=dark; st.rerun()
    st.markdown("---")
    pend_label=f"📩 Demandes ({nb_pend})" if nb_pend>0 else "📩 Demandes"
    menu=st.radio("Navigation",[
        "📊 Tableau de bord",pend_label,"🎯 Objectifs","🔍 Recherche",
        "👤 Acheteurs","🔎 Profil Acheteur","📋 Commandes","💰 Commissions","⚙️ Paramètres"
    ],label_visibility="collapsed")
    st.markdown("---")
    _da=get_acheteurs(); _dc=get_commandes()
    st.caption(f"{len(_da)} acheteurs · {len(_dc)} commandes")
    if nb_pend>0: st.caption(f"🔴 {nb_pend} demande(s) en attente")
    st.markdown("---")
    if st.button("🚪 Déconnexion",use_container_width=True):
        st.session_state['authenticated']=False; st.session_state['username']=""; st.rerun()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📊 TABLEAU DE BORD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if menu=="📊 Tableau de bord":
    ct,cb=st.columns([6,1])
    with ct: st.markdown("# 📊 Tableau de bord")
    with cb:
        st.markdown("")
        if st.button("➕",key="fab",use_container_width=True):
            st.session_state['show_new_order']=not st.session_state['show_new_order']; st.rerun()

    if nb_pend>0:
        st.warning(f"📩 **{nb_pend} demande(s) client en attente**")

    if st.session_state.get('show_new_order'):
        with st.expander("⚡ Nouvelle commande rapide",expanded=True):
            with st.form("qo",clear_on_submit=True):
                q1,q2=st.columns(2)
                with q1: qa=st.text_input("Acheteur (créé auto)"); qb=st.text_input("Boutique *")
                with q2: qm=st.number_input("Montant (€)",0.0,step=0.5); qt=st.radio("Commission",["En %","Fixe €"],horizontal=True)
                q3,q4=st.columns(2)
                with q3:
                    if qt=="En %": qp=st.number_input("Commission %",0.0,100.0,step=1.0); qe=0.0
                    else: qe=st.number_input("Commission €",0.0,step=0.5); qp=0.0
                with q4:
                    qs=st.selectbox("Statut",["En cours","Validée","Livrée","Annulée"])
                    q_tech=st.multiselect("Technique",TECHNIQUES)
                qn=st.text_input("Notes")
                q_couts=render_couts_form("qo")
                if st.form_submit_button("✅ Enregistrer",use_container_width=True):
                    if not qa.strip(): st.error("Acheteur requis.")
                    elif not qb.strip(): st.error("Boutique requise.")
                    elif qm<=0: st.error("Montant > 0.")
                    else:
                        mode="pct" if qt=="En %" else "fixe"
                        cv,_,ct_=ajouter_commande(qa,qb,qm,mode,qp,qe,qn,qs,",".join(q_tech),q_couts)
                        st.success(f"✅ Commission: {cv:.2f} € · Coûts: {ct_:.2f} €"); st.session_state['show_new_order']=False; st.rerun()
        st.markdown("---")

    df_cmd=get_commandes()
    nb_ach=len(get_acheteurs()); nb_cmd=len(df_cmd)
    av,rc=get_finance_summary(df_cmd)
    ca=df_cmd["montant_total"].sum() if not df_cmd.empty else 0
    total_couts=df_cmd["cout_total"].sum() if not df_cmd.empty else 0
    pm=ca/nb_cmd if nb_cmd else 0

    c1,c2,c3,c4=st.columns(4)
    c1.metric("Acheteurs",nb_ach); c2.metric("Commandes",nb_cmd)
    c3.metric("CA Total",f"{ca:,.2f} €"); c4.metric("Panier Moyen",f"{pm:,.2f} €")
    st.markdown("")
    c5,c6,c7=st.columns(3)
    c5.metric("💸 À venir",f"{av:,.2f} €"); c6.metric("✅ Reçu",f"{rc:,.2f} €"); c7.metric("📉 Coûts totaux",f"{total_couts:,.2f} €")

    obj=get_objectif_mois(datetime.now().strftime("%Y-%m"))
    if obj and obj['objectif_ca']>0 and not df_cmd.empty:
        st.divider(); st.markdown("### 🎯 Objectif du mois")
        dm=df_cmd[pd.to_datetime(df_cmd['date']).dt.strftime("%Y-%m")==datetime.now().strftime("%Y-%m")]
        cam=dm['montant_total'].sum() if not dm.empty else 0
        p_=min((cam/obj['objectif_ca'])*100,100)
        co_="#22c55e" if p_>=75 else "#f59e0b" if p_>=40 else "#ef4444"
        st.markdown(f"**CA :** {cam:,.2f} € / {obj['objectif_ca']:,.2f} €")
        st.markdown(f'<div class="obj-bar-bg"><div class="obj-bar-fill" style="width:{p_}%;background:{co_};">{p_:.0f}%</div></div>',unsafe_allow_html=True)

    if not df_cmd.empty:
        st.divider()
        t1,t2,t3=st.tabs(["📈 Évolution CA","🏪 Top Boutiques","👥 Top Acheteurs"])
        with t1:
            dfc=df_cmd.copy(); dfc['date']=pd.to_datetime(dfc['date'])
            dfc=dfc.set_index('date').resample('D')['montant_total'].sum().reset_index()
            dfc.columns=['Date','CA (€)']; dfc=dfc[dfc['CA (€)']>0]
            if not dfc.empty: st.bar_chart(dfc.set_index('Date'),y='CA (€)',color="#6366f1")
        with t2:
            tb=df_cmd.groupby('boutique')['montant_total'].sum().sort_values(ascending=False).head(8)
            if not tb.empty: st.bar_chart(tb,color="#22c55e")
        with t3:
            ta=df_cmd.groupby('acheteur')['montant_total'].sum().sort_values(ascending=False).head(8)
            if not ta.empty: st.bar_chart(ta,color="#f59e0b")
        st.divider(); st.markdown("### 🕐 Dernières commandes")
        st.dataframe(df_cmd[["date","acheteur","boutique","montant_total","commission_vendeur_eur","technique","cout_total","statut"]].head(10).rename(
            columns={"date":"Date","acheteur":"Acheteur","boutique":"Boutique","montant_total":"Montant (€)","commission_vendeur_eur":"Commission (€)","technique":"Technique","cout_total":"Coûts (€)","statut":"Statut"}),
            use_container_width=True,hide_index=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📩 DEMANDES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
elif menu.startswith("📩"):
    st.markdown("# 📩 Demandes Clients")
    st.caption("Formulaire client séparé → les demandes arrivent ici.")
    tab_att,tab_hist=st.tabs([f"⏳ En attente ({nb_pend})","📜 Historique"])
    with tab_att:
        dfp=get_demandes("En attente")
        if dfp.empty: st.info("Aucune demande en attente. 🎉")
        else:
            for _,dem in dfp.iterrows():
                st.markdown(f"""<div class="pending-card"><h4>📩 #{dem['id']} — {dem['nom_client']}</h4>
                <p>🛍️ <b>{dem['boutique']}</b> · 💶 <b>{dem['montant']:.2f} €</b><br>
                📞 {dem['telephone'] or '—'} · 📧 {dem['email'] or '—'}<br>
                📅 {dem['date_soumission']}</p></div>""",unsafe_allow_html=True)
                if dem['notes_client']: st.caption(f"💬 {dem['notes_client']}")
                if dem['identifiants']:
                    with st.expander(f"🔐 Identifiants #{dem['id']}"): st.code(dem['identifiants'],language=None)

                with st.expander(f"✅ Valider #{dem['id']}"):
                    with st.form(f"val_{dem['id']}"):
                        vc1,vc2=st.columns(2)
                        with vc1:
                            vt=st.radio("Commission",["En %","Fixe €"],horizontal=True,key=f"vt{dem['id']}")
                            if vt=="En %": vp=st.number_input("Commission %",0.0,100.0,step=1.0,key=f"vp{dem['id']}"); ve=0.0
                            else: ve=st.number_input("Commission €",0.0,step=0.5,key=f"ve{dem['id']}"); vp=0.0
                        with vc2:
                            v_tech=st.multiselect("Technique",TECHNIQUES,key=f"vtec{dem['id']}")
                        v_couts=render_couts_form(f"v{dem['id']}")
                        v_notes=st.text_input("Notes admin",key=f"vn{dem['id']}")
                        if st.form_submit_button("✅ Valider & créer",use_container_width=True):
                            mode="pct" if vt=="En %" else "fixe"
                            notes_f=f"{dem['notes_client']} | {v_notes}".strip(" | ")
                            cv,cp,ct_=ajouter_commande(dem['nom_client'],dem['boutique'],dem['montant'],
                                mode,vp,ve,notes_f,"En cours",",".join(v_tech),v_couts,
                                contact=dem['telephone'],email=dem['email'],identifiants=dem['identifiants'])
                            valider_demande(int(dem['id']))
                            st.success(f"✅ Commission: {cv:.2f} € · Coûts: {ct_:.2f} €"); st.rerun()
                if st.button(f"❌ Rejeter #{dem['id']}",key=f"rej{dem['id']}"):
                    rejeter_demande(int(dem['id'])); st.rerun()
                st.markdown("---")
    with tab_hist:
        dfh=get_demandes()
        dfh=dfh[dfh['statut']!="En attente"]
        if dfh.empty: st.info("Aucun historique.")
        else:
            st.dataframe(dfh[['id','date_soumission','nom_client','boutique','montant','statut']].rename(
                columns={'id':'ID','date_soumission':'Date','nom_client':'Client','boutique':'Boutique','montant':'Montant (€)','statut':'Statut'}),
                use_container_width=True,hide_index=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎯 OBJECTIFS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
elif menu=="🎯 Objectifs":
    st.markdown("# 🎯 Objectifs mensuels")
    with st.form("f_obj"):
        m=st.text_input("Mois (YYYY-MM)",value=datetime.now().strftime("%Y-%m"))
        o1,o2=st.columns(2)
        with o1: oca=st.number_input("Objectif CA (€)",0.0,step=100.0)
        with o2: ocmd=st.number_input("Objectif commandes",0,step=1)
        if st.form_submit_button("💾 Sauvegarder",use_container_width=True):
            set_objectif_mois(m,oca,ocmd); st.success(f"Objectif **{m}** enregistré !"); st.rerun()
    conn=get_conn(); dfo=pd.read_sql_query("SELECT * FROM objectifs ORDER BY mois DESC",conn); conn.close()
    if not dfo.empty:
        st.divider(); dfc=get_commandes()
        for _,ro in dfo.iterrows():
            m=ro['mois']
            if not dfc.empty:
                dm=dfc[pd.to_datetime(dfc['date']).dt.strftime("%Y-%m")==m]
                car=dm['montant_total'].sum() if not dm.empty else 0
            else: car=0
            p=(car/ro['objectif_ca']*100) if ro['objectif_ca']>0 else 0
            co="#22c55e" if p>=100 else "#f59e0b" if p>=50 else "#ef4444"
            st.markdown(f"**{'✅' if p>=100 else '⏳'} {m}** — {car:,.2f} € / {ro['objectif_ca']:,.2f} € ({p:.0f}%)")
            st.markdown(f'<div class="obj-bar-bg"><div class="obj-bar-fill" style="width:{min(p,100)}%;background:{co};">{p:.0f}%</div></div>',unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔍 RECHERCHE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
elif menu=="🔍 Recherche":
    st.markdown("# 🔍 Recherche globale")
    terme=st.text_input("🔎",placeholder="Nom, boutique, note...")
    if terme and len(terme)>=2:
        res=recherche_globale(terme)
        if res.empty: st.warning("Aucun résultat.")
        else:
            st.success(f"**{len(res)}** résultat(s)")
            for tr in res['type'].unique():
                st.markdown(f"### {'👤' if tr=='Acheteur' else '📦' if tr=='Commande' else '💬'} {tr}s")
                for _,r in res[res['type']==tr].iterrows():
                    st.markdown(f"**{r['titre']}** — {r['detail']} *(ID: {r['id']})*")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 👤 ACHETEURS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
elif menu=="👤 Acheteurs":
    st.markdown("# 👤 Acheteurs")
    ta,tl=st.tabs(["➕ Ajouter","📋 Liste"])
    with ta:
        with st.form("fa",clear_on_submit=True):
            c1,c2=st.columns(2)
            with c1: nom=st.text_input("Nom *"); contact=st.text_input("Téléphone"); email=st.text_input("Email")
            with c2: adresse=st.text_input("Adresse"); parrain=st.text_input("Parrain (vide si aucun)"); cp=st.number_input("Commission parrain (%)",0.0,100.0,step=1.0)
            if st.form_submit_button("✅ Ajouter",use_container_width=True):
                if not nom.strip(): st.error("Nom requis.")
                else:
                    ok,msg=ajouter_acheteur(nom,contact,parrain,cp,email,adresse)
                    if ok: st.success(f"**{nom}** ajouté !"); st.rerun()
                    else: st.error(msg)
    with tl:
        dfa=get_acheteurs()
        if dfa.empty: st.info("Aucun acheteur.")
        else:
            rech=st.text_input("🔎 Filtrer",key="fa_f")
            if rech: dfa=dfa[dfa['nom'].str.contains(rech,case=False,na=False)]
            st.dataframe(dfa[['nom','contact','email','parrain','commission_parrain','date_creation']].rename(
                columns={'nom':'Nom','contact':'Tél.','email':'Email','parrain':'Parrain','commission_parrain':'Comm. (%)','date_creation':'Inscrit'}),
                use_container_width=True,hide_index=True)
            st.markdown("---")
            cd1,cd2=st.columns([3,1])
            with cd1: a_s=st.selectbox("Supprimer",dfa['nom'].tolist(),key="da")
            with cd2:
                st.markdown(""); st.markdown("")
                if st.button("🗑️",key="bda"):
                    r=dfa[dfa['nom']==a_s].iloc[0]; supprimer_acheteur(int(r['id'])); st.success(f"**{a_s}** supprimé."); st.rerun()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔎 PROFIL ACHETEUR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
elif menu=="🔎 Profil Acheteur":
    st.markdown("# 🔎 Profil Acheteur")
    dfa=get_acheteurs()
    if dfa.empty: st.warning("Aucun acheteur.")
    else:
        an=st.selectbox("Sélectionnez",dfa['nom'].tolist())
        ar=dfa[dfa['nom']==an].iloc[0]; aid=int(ar['id'])
        pt=ar['parrain']
        badge=f'<span class="badge">Parrain : {pt} ({ar["commission_parrain"]}%)</span>' if pt!="Aucun" else '<span class="badge">Pas de parrain</span>'
        st.markdown(f"""<div class="profil-card"><h3>👤 {ar['nom']}</h3>
            <p>📞 {ar['contact'] or '—'} · 📧 {ar['email'] or '—'}</p>
            <p>📍 {ar['adresse'] or '—'}</p><p>📅 Inscrit le {ar['date_creation']}</p>{badge}</div>""",unsafe_allow_html=True)
        if ar['identifiants_boutique']:
            st.markdown("### 🔐 Accès Boutique")
            st.markdown(f'<div class="cred-box">{ar["identifiants_boutique"]}</div>',unsafe_allow_html=True)
        dfh=get_commandes(aid)
        if not dfh.empty:
            tot=dfh['montant_total'].sum(); nb=len(dfh); av,rc=get_finance_summary(dfh)
            total_c=dfh['cout_total'].sum()
            st.markdown(f"""<div class="kpi-row">
                <div class="kpi-mini"><div class="value">{nb}</div><div class="label">Commandes</div></div>
                <div class="kpi-mini"><div class="value">{tot:,.2f} €</div><div class="label">Total</div></div>
                <div class="kpi-mini"><div class="value">{av:,.2f} €</div><div class="label">À venir</div></div>
                <div class="kpi-mini"><div class="value">{rc:,.2f} €</div><div class="label">Reçu</div></div>
                <div class="kpi-mini"><div class="value">{total_c:,.2f} €</div><div class="label">Coûts</div></div>
            </div>""",unsafe_allow_html=True)
            st.markdown("### Historique")
            st.dataframe(dfh[['date','boutique','montant_total','commission_vendeur_eur','technique','cout_total','statut']].rename(
                columns={'date':'Date','boutique':'Boutique','montant_total':'Montant (€)','commission_vendeur_eur':'Commission (€)','technique':'Technique','cout_total':'Coûts (€)','statut':'Statut'}),
                use_container_width=True,hide_index=True)
        else: st.info("Aucun achat.")
        st.divider(); st.markdown("### 💬 Notes")
        with st.form("fn",clear_on_submit=True):
            nt=st.text_area("Ajouter une note")
            if st.form_submit_button("💬 Ajouter",use_container_width=True):
                if nt.strip(): ajouter_note(aid,nt,st.session_state['username']); st.success("Ajoutée !"); st.rerun()
        dfn=get_notes(aid)
        if not dfn.empty:
            for _,n in dfn.iterrows():
                st.markdown(f'<div class="note-bubble"><div class="note-date">📝 {n["auteur"]} — {n["date_creation"]}</div>{n["contenu"]}</div>',unsafe_allow_html=True)
            with st.expander("🗑️ Supprimer une note"):
                nids=dfn['id'].tolist(); nlabs=[f"#{n['id']} — {n['contenu'][:40]}..." for _,n in dfn.iterrows()]
                sn=st.selectbox("Note",nids,format_func=lambda x: nlabs[nids.index(x)])
                if st.button("Supprimer"): supprimer_note(sn); st.rerun()
        st.divider()
        with st.expander("✏️ Modifier"):
            with st.form("fe"):
                ec1,ec2=st.columns(2)
                with ec1: nn=st.text_input("Nom",value=ar['nom']); nc=st.text_input("Tél.",value=ar['contact']); ne=st.text_input("Email",value=ar['email']); na=st.text_input("Adresse",value=ar['adresse'])
                with ec2: np=st.text_input("Parrain",value=ar['parrain'] if ar['parrain']!="Aucun" else ""); nco=st.number_input("Comm. (%)",value=float(ar['commission_parrain']),min_value=0.0,max_value=100.0); nid=st.text_area("Identifiants boutique",value=ar['identifiants_boutique'])
                if st.form_submit_button("💾 Sauvegarder",use_container_width=True):
                    ok,msg=modifier_acheteur(aid,nn,nc,ne,na,np,nco,nid)
                    if ok: st.success("Mis à jour !"); st.rerun()
                    else: st.error(msg)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📋 COMMANDES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
elif menu=="📋 Commandes":
    ct,cb=st.columns([5,1])
    with ct: st.markdown("# 📋 Commandes")
    with cb:
        st.markdown("")
        if st.button("➕",key="nc",use_container_width=True):
            st.session_state['show_new_order_page']=not st.session_state.get('show_new_order_page',False); st.rerun()

    if st.session_state.get('show_new_order_page'):
        with st.expander("⚡ Nouvelle commande",expanded=True):
            with st.form("fcmd",clear_on_submit=True):
                p1,p2=st.columns(2)
                with p1: pa=st.text_input("Acheteur (créé auto)"); pb=st.text_input("Boutique *"); pm_=st.number_input("Montant (€)",0.0,step=0.5)
                with p2:
                    pt_=st.radio("Commission",["En %","Fixe €"],horizontal=True)
                    if pt_=="En %": pp=st.number_input("Commission %",0.0,100.0,step=1.0); pe=0.0
                    else: pe=st.number_input("Commission €",0.0,step=0.5); pp=0.0
                    ps=st.selectbox("Statut",["En cours","Validée","Livrée","Annulée"])
                p3,p4=st.columns(2)
                with p3: pn=st.text_input("Notes"); p_tech=st.multiselect("Technique",TECHNIQUES)
                with p4: pr=st.checkbox("Récurrente"); pf=st.selectbox("Fréquence",["Hebdo (7j)","Bi-mens. (14j)","Mens. (30j)","Trim. (90j)"])
                fmap={"Hebdo (7j)":7,"Bi-mens. (14j)":14,"Mens. (30j)":30,"Trim. (90j)":90}
                st.markdown("---")
                p_couts=render_couts_form("ncmd")
                if st.form_submit_button("✅ Enregistrer",use_container_width=True):
                    if not pa.strip(): st.error("Acheteur requis.")
                    elif not pb.strip(): st.error("Boutique requise.")
                    elif pm_<=0: st.error("Montant > 0.")
                    else:
                        mode="pct" if pt_=="En %" else "fixe"
                        cv,_,ct_=ajouter_commande(pa,pb,pm_,mode,pp,pe,pn,ps,",".join(p_tech),p_couts,pr,fmap[pf] if pr else 0)
                        st.success(f"✅ Commission: {cv:.2f} € · Coûts: {ct_:.2f} €"); st.session_state['show_new_order_page']=False; st.rerun()
        st.markdown("---")

    dfc=get_commandes()
    if dfc.empty: st.info("Aucune commande.")
    else:
        st.markdown("#### 🔎 Filtres")
        cf1,cf2,cf3=st.columns(3)
        with cf1: fa=st.multiselect("Acheteur",dfc['acheteur'].unique().tolist())
        with cf2: fb=st.multiselect("Boutique",dfc['boutique'].unique().tolist())
        with cf3: fs=st.multiselect("Statut",dfc['statut'].unique().tolist())
        # Filtre technique
        ft=st.multiselect("Technique",TECHNIQUES,key="filt_tech")

        df_f=dfc.copy()
        if fa: df_f=df_f[df_f['acheteur'].isin(fa)]
        if fb: df_f=df_f[df_f['boutique'].isin(fb)]
        if fs: df_f=df_f[df_f['statut'].isin(fs)]
        if ft: df_f=df_f[df_f['technique'].apply(lambda x: any(t in str(x) for t in ft))]

        av,rc=get_finance_summary(df_f)
        total_couts=df_f['cout_total'].sum() if not df_f.empty else 0
        st.markdown(f"**{len(df_f)}** commande(s)")
        s1,s2,s3,s4=st.columns(4)
        s1.metric("CA",f"{df_f['montant_total'].sum():,.2f} €"); s2.metric("💸 À venir",f"{av:,.2f} €")
        s3.metric("✅ Reçu",f"{rc:,.2f} €"); s4.metric("📉 Coûts",f"{total_couts:,.2f} €")
        st.divider()
        dcols=['id','date','acheteur','boutique','montant_total','commission_vendeur_eur','technique','cout_total','statut','notes']
        rmap={'id':'ID','date':'Date','acheteur':'Acheteur','boutique':'Boutique','montant_total':'Montant (€)',
              'commission_vendeur_eur':'Commission (€)','technique':'Technique','cout_total':'Coûts (€)','statut':'Statut','notes':'Notes'}
        st.dataframe(df_f[dcols].rename(columns=rmap),use_container_width=True,hide_index=True)
        st.divider()
        e1,e2=st.columns(2)
        with e1: st.download_button("📄 CSV",export_df(df_f[dcols].rename(columns=rmap),"csv"),"commandes.csv","text/csv",use_container_width=True)
        with e2: st.download_button("📊 Excel",export_df(df_f[dcols].rename(columns=rmap),"xlsx"),"commandes.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)

        # Détail d'une commande
        st.divider(); st.markdown("### 🔍 Détail d'une commande")
        detail_id=st.number_input("ID",min_value=1,step=1,key="detail_id")
        if detail_id in dfc['id'].values:
            cr=dfc[dfc['id']==detail_id].iloc[0]
            st.markdown(f"**{cr['acheteur']}** — {cr['boutique']} — {cr['montant_total']:.2f} € — *{cr['statut']}*")
            if cr['technique']:
                st.markdown(f"Techniques : {render_technique_badges(cr['technique'])}",unsafe_allow_html=True)
            st.markdown("**Coûts :**")
            render_couts_display(cr['couts_details'],cr['cout_total'])

            # Profit = commission - coûts
            profit=cr['commission_vendeur_eur']-cr['cout_total']
            color_profit="#22c55e" if profit>=0 else "#ef4444"
            st.markdown(f"**Profit net : <span style='color:{color_profit};font-weight:700;'>{profit:.2f} €</span>**",unsafe_allow_html=True)

        # Modifier
        st.divider(); st.markdown("### ✏️ Modifier une commande")
        eid=st.number_input("ID commande à modifier",min_value=1,step=1,key="eid")
        if eid in dfc['id'].values:
            cr=dfc[dfc['id']==eid].iloc[0]
            existing_couts={}
            try: existing_couts=json.loads(cr['couts_details']) if isinstance(cr['couts_details'],str) else cr['couts_details']
            except: pass
            with st.form("fedit"):
                ec1,ec2=st.columns(2)
                with ec1:
                    eb=st.text_input("Boutique",value=cr['boutique']); em=st.number_input("Montant (€)",value=float(cr['montant_total']),min_value=0.0,step=0.5)
                    et=st.radio("Commission",["En %","Fixe €"],horizontal=True,index=0 if cr['commission_mode']=='pct' else 1)
                    if et=="En %": epp=st.number_input("Commission %",value=float(cr['commission_vendeur_pct']),min_value=0.0,max_value=100.0,step=1.0); eee=0.0
                    else: eee=st.number_input("Commission €",value=float(cr['commission_vendeur_eur']),min_value=0.0,step=0.5); epp=0.0
                with ec2:
                    es=st.selectbox("Statut",["En cours","Validée","Livrée","Annulée"],index=["En cours","Validée","Livrée","Annulée"].index(cr['statut']))
                    existing_techs=[t.strip() for t in str(cr['technique']).split(",") if t.strip()]
                    e_tech=st.multiselect("Technique",TECHNIQUES,default=[t for t in existing_techs if t in TECHNIQUES])
                    en=st.text_input("Notes",value=cr['notes'])
                st.markdown("---")
                e_couts=render_couts_form(f"edit{eid}",existing_couts)
                if st.form_submit_button("💾 Sauvegarder",use_container_width=True):
                    mode="pct" if et=="En %" else "fixe"
                    modifier_commande(int(eid),eb,em,mode,epp,eee,en,es,",".join(e_tech),e_couts)
                    st.success(f"#{eid} mise à jour !"); st.rerun()

        st.divider()
        d1,d2=st.columns([3,1])
        with d1: did=st.number_input("ID à supprimer",min_value=1,step=1,key="did")
        with d2:
            st.markdown(""); st.markdown("")
            if st.button("🗑️ Supprimer",key="bd"):
                if did in dfc['id'].values: supprimer_commande(int(did)); st.success(f"#{did} supprimée."); st.rerun()
                else: st.error("Introuvable.")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 💰 COMMISSIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
elif menu=="💰 Commissions":
    st.markdown("# 💰 Commissions")
    dfc=get_commandes()
    if dfc.empty: st.info("Aucune commande.")
    else:
        av,rc=get_finance_summary(dfc)
        total_couts=dfc['cout_total'].sum()
        c1,c2,c3=st.columns(3)
        c1.metric("💸 À venir",f"{av:,.2f} €"); c2.metric("✅ Reçu",f"{rc:,.2f} €"); c3.metric("📉 Coûts totaux",f"{total_couts:,.2f} €")
        t1,t2,t3=st.tabs(["🤝 Parrains","📊 Par boutique","🔧 Par technique"])
        with t1:
            dp=dfc[dfc['parrain']!="Aucun"]
            if dp.empty: st.info("Aucune commission parrainage.")
            else:
                rec=dp.groupby('parrain').agg(Filleuls=('acheteur','nunique'),Commandes=('id','count'),CA=('montant_total','sum'),Commissions=('commission_parrain_eur','sum')).reset_index().rename(columns={'parrain':'Parrain'}).sort_values('Commissions',ascending=False)
                st.metric("Total dû",f"{rec['Commissions'].sum():,.2f} €")
                st.dataframe(rec,use_container_width=True,hide_index=True)
                st.bar_chart(rec.set_index('Parrain')['Commissions'],color="#8b5cf6")
                e1,e2=st.columns(2)
                with e1: st.download_button("📄 CSV",export_df(rec,"csv"),"commissions.csv","text/csv",use_container_width=True)
                with e2: st.download_button("📊 Excel",export_df(rec,"xlsx"),"commissions.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
        with t2:
            rb=dfc.groupby('boutique').agg(Cmd=('id','count'),CA=('montant_total','sum'),Commission=('commission_vendeur_eur','sum'),Couts=('cout_total','sum')).reset_index()
            rb['Profit']=rb['Commission']-rb['Couts']
            rb=rb.sort_values('Profit',ascending=False).rename(columns={'boutique':'Boutique'})
            st.dataframe(rb,use_container_width=True,hide_index=True)
            st.bar_chart(rb.set_index('Boutique')['Profit'],color="#22c55e")
        with t3:
            # Stats par technique
            st.markdown("### Répartition par technique")
            tech_data=[]
            for t in TECHNIQUES:
                df_t=dfc[dfc['technique'].str.contains(t,na=False)]
                if not df_t.empty:
                    tech_data.append({"Technique":t,"Commandes":len(df_t),"CA":df_t['montant_total'].sum(),
                                     "Commission":df_t['commission_vendeur_eur'].sum(),"Coûts":df_t['cout_total'].sum()})
            if tech_data:
                df_tech=pd.DataFrame(tech_data)
                df_tech['Profit']=df_tech['Commission']-df_tech['Coûts']
                st.dataframe(df_tech,use_container_width=True,hide_index=True)
                st.bar_chart(df_tech.set_index('Technique')['Profit'],color="#6366f1")
            else: st.info("Aucune technique utilisée.")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚙️ PARAMÈTRES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
elif menu=="⚙️ Paramètres":
    st.markdown("# ⚙️ Paramètres")
    tp,ti=st.tabs(["🔐 Mot de passe","ℹ️ À propos"])
    with tp:
        with st.form("fpw"):
            op=st.text_input("Actuel",type="password"); n1=st.text_input("Nouveau",type="password"); n2=st.text_input("Confirmer",type="password")
            if st.form_submit_button("🔐 Modifier",use_container_width=True):
                if not auth_check(st.session_state['username'],op): st.error("Incorrect.")
                elif n1!=n2: st.error("Ne correspondent pas.")
                elif len(n1)<4: st.error("Min. 4 caractères.")
                else: change_pw(st.session_state['username'],n1); st.success("Modifié !")
    with ti:
        st.markdown("""
### ⚡ SalesFlow v5.0

**Fonctionnalités :**
- 📩 Formulaire client séparé (site indépendant)
- ✅ File de validation des demandes
- 🔧 Techniques par commande (FTID, LIT, RTS, DNA, EB)
- 💰 Coûts détaillés par catégorie (FTID, LIT, RTS) + total auto
- 📊 Stats par technique avec profit
- Commission % ou montant fixe · À venir / Reçu
- Création auto d'acheteurs · Identifiants boutique
- Notes · Récurrences · Objectifs · Recherche · Export · Mode sombre
        """)
