import streamlit as st
import pandas as pd
import libsql_client
import hashlib
import io
from datetime import datetime, timedelta

TURSO_URL = "libsql://app-jeasaa.aws-eu-west-1.turso.io"
TURSO_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3NzMwNjM0ODksImlkIjoiMDE5Y2QyY2UtZmUwMS03YjYyLTk4MjEtN2M1NjcxNjBiMDBmIiwicmlkIjoiMmVlNTYwNTYtMmJkZC00NmMzLTllZmEtODY3Yjc1MGI5ZmMyIn0.W5_YArM9r3v7hd8fy65ZRf5ya2xrPhmmmref4NdCUmhR8j6XytZ2_g73yALIJC8C5h9n-1BzBkix9X3FQ_yOAA"
TECHNIQUES = ["FTID", "LIT", "RTS", "DNA", "EB"]

st.set_page_config(page_title="SalesFlow", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")
for k, v in [('authenticated',False),('username',''),('dark_mode',False),('show_new_order',False),('show_new_order_page',False)]:
    if k not in st.session_state: st.session_state[k] = v

# ━━━ DB HELPERS ━━━
def db():
    return libsql_client.create_client_sync(url=TURSO_URL, auth_token=TURSO_TOKEN)

def run(sql, params=None):
    client = db()
    if params: rs = client.execute(sql, params)
    else: rs = client.execute(sql)
    client.close()
    return rs

def query_df(sql, params=None):
    client = db()
    if params: rs = client.execute(sql, params)
    else: rs = client.execute(sql)
    client.close()
    if not rs.columns: return pd.DataFrame()
    return pd.DataFrame(rs.rows, columns=rs.columns)

def query_val(sql, params=None):
    """Retourne la première valeur du premier row."""
    client = db()
    if params: rs = client.execute(sql, params)
    else: rs = client.execute(sql)
    client.close()
    if rs.rows: return rs.rows[0][0]
    return None

# ━━━ CSS ━━━
def inject_css(dark=False):
    if dark:
        bg="#0b1120";text="#f9fafb";text2="#d1d5db";text3="#9ca3af";accent="#6366f1";accent2="#4f46e5"
        card_border="#374151";metric_bg="linear-gradient(135deg,#111827,#1f2937)"
        sidebar_bg="linear-gradient(195deg,#0b1120,#1e1b4b)"
        form_bg="#111827";form_border="#374151";kpi_bg="#1f2937"
        input_bg="#1f2937";input_border="#374151";input_text="#f9fafb"
        profil_bg="linear-gradient(135deg,#1e1b4b,#312e81)";badge_bg="rgba(99,102,241,0.2)";badge_text="#a5b4fc";bg3="#1f2937"
    else:
        bg="#f8fafc";text="#0f172a";text2="#334155";text3="#64748b";accent="#6366f1";accent2="#4f46e5"
        card_border="#e2e8f0";metric_bg="linear-gradient(135deg,#ffffff,#f1f5f9)"
        sidebar_bg="linear-gradient(195deg,#0f172a,#1e1b4b)"
        form_bg="#ffffff";form_border="#e2e8f0";kpi_bg="#f1f5f9"
        input_bg="#ffffff";input_border="#cbd5e1";input_text="#0f172a"
        profil_bg="linear-gradient(135deg,#1e1b4b,#312e81)";badge_bg="rgba(99,102,241,0.1)";badge_text="#6366f1";bg3="#f1f5f9"

    st.markdown(f"""<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    html,body,[class*="css"]{{font-family:'Outfit',sans-serif;}}
    .stApp{{background:{bg};}}
    section[data-testid="stSidebar"]{{background:{sidebar_bg};}}
    section[data-testid="stSidebar"] *{{color:#e2e8f0 !important;}}
    div[data-testid="stMetric"]{{background:{metric_bg};border:1px solid {card_border};border-radius:16px;padding:20px 24px;transition:transform .15s;}}
    div[data-testid="stMetric"]:hover{{transform:translateY(-2px);}}
    div[data-testid="stMetric"] label{{color:{text3} !important;font-weight:600;font-size:0.8rem !important;text-transform:uppercase;letter-spacing:0.8px;}}
    div[data-testid="stMetric"] [data-testid="stMetricValue"]{{color:{text} !important;font-weight:700;font-family:'JetBrains Mono',monospace !important;}}
    .stButton>button{{background:linear-gradient(135deg,{accent},{accent2});color:white;border:none;border-radius:10px;font-weight:600;padding:0.55rem 1.6rem;}}
    .stButton>button:hover{{box-shadow:0 4px 16px rgba(99,102,241,0.3);transform:translateY(-1px);}}
    .stForm{{background:{form_bg};border:1px solid {form_border};border-radius:16px;padding:28px;}}
    .stTextInput input,.stNumberInput input,.stTextArea textarea{{background:{input_bg} !important;color:{input_text} !important;border-color:{input_border} !important;border-radius:10px !important;}}
    .stSelectbox>div>div{{background:{input_bg} !important;border-radius:10px !important;}}
    h1{{color:{text};font-weight:800 !important;}} h2,h3{{color:{text2};font-weight:700 !important;}}
    p,li,span,label,.stMarkdown{{color:{text2};}}
    hr{{border-color:{card_border} !important;}}
    .profil-card{{background:{profil_bg};color:white;border-radius:20px;padding:32px;margin-bottom:24px;}}
    .profil-card h3{{color:#f8fafc !important;margin:0 0 16px 0;}}
    .profil-card p{{color:#c7d2fe;margin:4px 0;}}
    .profil-card .badge{{display:inline-block;background:{badge_bg};color:{badge_text};padding:5px 14px;border-radius:20px;font-size:0.82rem;font-weight:600;margin-top:10px;}}
    .kpi-row{{display:flex;gap:16px;margin:16px 0;}}
    .kpi-mini{{flex:1;background:{kpi_bg};border:1px solid {card_border};border-radius:14px;padding:18px;text-align:center;}}
    .kpi-mini .value{{font-size:1.6rem;font-weight:700;color:{text};font-family:'JetBrains Mono',monospace;}}
    .kpi-mini .label{{font-size:0.75rem;color:{text3};text-transform:uppercase;letter-spacing:0.8px;margin-top:6px;font-weight:600;}}
    .note-bubble{{background:{kpi_bg};border-left:4px solid {accent};border-radius:0 14px 14px 0;padding:14px 18px;margin:10px 0;}}
    .note-bubble .note-date{{font-size:0.75rem;color:{text3};margin-bottom:6px;}}
    .cred-box{{background:{kpi_bg};border:1px solid {card_border};border-radius:14px;padding:18px;margin:8px 0;font-family:'JetBrains Mono',monospace;font-size:0.88rem;white-space:pre-wrap;}}
    .pending-card{{background:{kpi_bg};border:1px solid {card_border};border-radius:16px;padding:24px;margin:16px 0;}}
    .pending-card h4{{color:{text};margin:0 0 12px 0;}}
    .obj-bar-bg{{background:{kpi_bg};border:1px solid {card_border};border-radius:12px;height:36px;overflow:hidden;margin:8px 0;}}
    .obj-bar-fill{{height:100%;border-radius:12px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:0.85rem;color:white;font-family:'JetBrains Mono',monospace;}}
    </style>""", unsafe_allow_html=True)

# ━━━ INIT ━━━
def init_db():
    tables = [
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT,username TEXT NOT NULL UNIQUE,password_hash TEXT NOT NULL,role TEXT DEFAULT 'admin',created_at TEXT)",
        "CREATE TABLE IF NOT EXISTS acheteurs (id INTEGER PRIMARY KEY AUTOINCREMENT,nom TEXT NOT NULL UNIQUE,parrain TEXT DEFAULT 'Aucun',commission_parrain REAL DEFAULT 0.0,identifiant_boutique TEXT DEFAULT '',mdp_boutique TEXT DEFAULT '',date_creation TEXT)",
        "CREATE TABLE IF NOT EXISTS commandes (id INTEGER PRIMARY KEY AUTOINCREMENT,date TEXT,acheteur_id INTEGER NOT NULL,boutique TEXT NOT NULL,montant_total REAL NOT NULL,commission_mode TEXT DEFAULT 'pct',commission_vendeur_pct REAL DEFAULT 0.0,commission_vendeur_eur REAL NOT NULL,commission_parrain_eur REAL DEFAULT 0.0,notes TEXT DEFAULT '',statut TEXT DEFAULT 'En cours',technique TEXT DEFAULT '',cout_total REAL DEFAULT 0.0,est_recurrente INTEGER DEFAULT 0,frequence_jours INTEGER DEFAULT 0,prochaine_date TEXT DEFAULT '')",
        "CREATE TABLE IF NOT EXISTS notes_acheteurs (id INTEGER PRIMARY KEY AUTOINCREMENT,acheteur_id INTEGER NOT NULL,contenu TEXT NOT NULL,date_creation TEXT,auteur TEXT DEFAULT 'admin')",
        "CREATE TABLE IF NOT EXISTS objectifs (id INTEGER PRIMARY KEY AUTOINCREMENT,mois TEXT NOT NULL UNIQUE,objectif_ca REAL DEFAULT 0.0,objectif_commandes INTEGER DEFAULT 0)",
        "CREATE TABLE IF NOT EXISTS demandes (id INTEGER PRIMARY KEY AUTOINCREMENT,date_soumission TEXT,nom_client TEXT NOT NULL,boutique TEXT NOT NULL,montant REAL NOT NULL,identifiant_boutique TEXT DEFAULT '',mdp_boutique TEXT DEFAULT '',notes_client TEXT DEFAULT '',statut TEXT DEFAULT 'En attente')",
        "CREATE TABLE IF NOT EXISTS couts_techniques (id INTEGER PRIMARY KEY AUTOINCREMENT,nom TEXT NOT NULL UNIQUE,prix REAL NOT NULL DEFAULT 0.0)",
    ]
    for t in tables: run(t)
    if query_val("SELECT COUNT(*) FROM users") == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        run("INSERT INTO users (username,password_hash,role,created_at) VALUES (?,?,?,?)",
            ["admin", hashlib.sha256("admin".encode()).hexdigest(), "admin", now])

# ━━━ AUTH ━━━
def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()
def auth_check(u,p): return len(query_df("SELECT * FROM users WHERE username=? AND password_hash=?",[u,hash_pw(p)]))>0
def change_pw(u,np): run("UPDATE users SET password_hash=? WHERE username=?",[hash_pw(np),u])

# ━━━ COÛTS ━━━
def get_couts(): return query_df("SELECT * FROM couts_techniques ORDER BY nom")
def set_cout(nom,prix):
    if query_val("SELECT id FROM couts_techniques WHERE nom=?",[nom]): run("UPDATE couts_techniques SET prix=? WHERE nom=?",[prix,nom])
    else: run("INSERT INTO couts_techniques (nom,prix) VALUES (?,?)",[nom,prix])
def del_cout(nom): run("DELETE FROM couts_techniques WHERE nom=?",[nom])
def get_prix(nom):
    v=query_val("SELECT prix FROM couts_techniques WHERE nom=?",[nom])
    return float(v) if v else 0.0
def calc_cout(tech):
    if not tech: return 0.0
    return sum(get_prix(t.strip()) for t in tech.split(",") if t.strip())

# ━━━ ACHETEURS ━━━
def get_or_create(nom,ident="",mdp=""):
    row=query_val("SELECT id FROM acheteurs WHERE nom=?",[nom.strip()])
    if row:
        if ident.strip(): run("UPDATE acheteurs SET identifiant_boutique=? WHERE id=? AND (identifiant_boutique IS NULL OR identifiant_boutique='')",[ident.strip(),int(row)])
        if mdp.strip(): run("UPDATE acheteurs SET mdp_boutique=? WHERE id=? AND (mdp_boutique IS NULL OR mdp_boutique='')",[mdp.strip(),int(row)])
        return int(row)
    now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rs=run("INSERT INTO acheteurs (nom,identifiant_boutique,mdp_boutique,date_creation) VALUES (?,?,?,?)",[nom.strip(),ident.strip(),mdp.strip(),now])
    return rs.last_insert_rowid

def add_ach(nom,parrain,cp,ident="",mdp=""):
    try:
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        run("INSERT INTO acheteurs (nom,parrain,commission_parrain,identifiant_boutique,mdp_boutique,date_creation) VALUES (?,?,?,?,?,?)",
            [nom.strip(),parrain.strip() if parrain.strip() else "Aucun",cp,ident.strip(),mdp.strip(),now])
        return True,"OK"
    except: return False,"Ce nom existe déjà."

def get_ach(): return query_df("SELECT * FROM acheteurs ORDER BY nom")
def del_ach(aid):
    run("DELETE FROM notes_acheteurs WHERE acheteur_id=?",[aid])
    run("DELETE FROM commandes WHERE acheteur_id=?",[aid])
    run("DELETE FROM acheteurs WHERE id=?",[aid])
def mod_ach(aid,nom,parrain,cp,ident,mdp):
    try:
        run("UPDATE acheteurs SET nom=?,parrain=?,commission_parrain=?,identifiant_boutique=?,mdp_boutique=? WHERE id=?",
            [nom.strip(),parrain.strip() if parrain.strip() else "Aucun",cp,ident.strip(),mdp.strip(),aid])
        return True,"OK"
    except: return False,"Ce nom existe déjà."

# ━━━ COMMANDES ━━━
def calc_comm(mont,mode,pct,eur,parr,cp):
    if mode=="pct": cv=mont*(pct/100);pf=pct
    else: cv=eur;pf=(eur/mont*100) if mont>0 else 0
    cpar=cv*(cp/100) if parr!="Aucun" and cp>0 else 0
    return cv,cpar,pf

def add_cmd(anom,bout,mont,cmode,cpct,ceur,notes,statut,tech,est_rec=False,fj=0,ident="",mdp=""):
    aid=get_or_create(anom,ident,mdp)
    ach=query_df("SELECT * FROM acheteurs WHERE id=?",[aid]).iloc[0]
    cv,cp,pf=calc_comm(mont,cmode,cpct,ceur,ach['parrain'],ach['commission_parrain'])
    cout=calc_cout(tech); now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    proch=""
    if est_rec and fj>0: proch=(datetime.now()+timedelta(days=fj)).strftime("%Y-%m-%d")
    run("""INSERT INTO commandes (date,acheteur_id,boutique,montant_total,commission_mode,commission_vendeur_pct,commission_vendeur_eur,commission_parrain_eur,notes,statut,technique,cout_total,est_recurrente,frequence_jours,prochaine_date) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        [now,aid,bout.strip(),mont,cmode,pf,cv,cp,notes.strip(),statut,tech,cout,1 if est_rec else 0,fj,proch])
    return cv,cp,cout

def mod_cmd(cid,bout,mont,cmode,cpct,ceur,notes,statut,tech):
    aid=query_val("SELECT acheteur_id FROM commandes WHERE id=?",[cid])
    if not aid: return
    ach=query_df("SELECT * FROM acheteurs WHERE id=?",[int(aid)]).iloc[0]
    cv,cp,pf=calc_comm(mont,cmode,cpct,ceur,ach['parrain'],ach['commission_parrain'])
    cout=calc_cout(tech)
    run("UPDATE commandes SET boutique=?,montant_total=?,commission_mode=?,commission_vendeur_pct=?,commission_vendeur_eur=?,commission_parrain_eur=?,notes=?,statut=?,technique=?,cout_total=? WHERE id=?",
        [bout.strip(),mont,cmode,pf,cv,cp,notes.strip(),statut,tech,cout,cid])

def get_cmd(aid=None):
    q="SELECT c.id,c.date,a.nom AS acheteur,c.boutique,c.montant_total,c.commission_mode,c.commission_vendeur_pct,c.commission_vendeur_eur,a.parrain,c.commission_parrain_eur,c.notes,c.statut,c.technique,c.cout_total,c.est_recurrente,c.frequence_jours,c.prochaine_date,c.acheteur_id FROM commandes c JOIN acheteurs a ON c.acheteur_id=a.id"
    if aid: return query_df(q+" WHERE c.acheteur_id=? ORDER BY c.date DESC",[aid])
    return query_df(q+" ORDER BY c.date DESC")

def del_cmd(cid): run("DELETE FROM commandes WHERE id=?",[cid])

# ━━━ DEMANDES ━━━
def get_dem(s=None):
    if s: return query_df("SELECT * FROM demandes WHERE statut=? ORDER BY date_soumission DESC",[s])
    return query_df("SELECT * FROM demandes ORDER BY date_soumission DESC")
def val_dem(did): run("UPDATE demandes SET statut='Validée' WHERE id=?",[did])
def rej_dem(did): run("UPDATE demandes SET statut='Rejetée' WHERE id=?",[did])
def cnt_pend(): return int(query_val("SELECT COUNT(*) FROM demandes WHERE statut='En attente'") or 0)

# ━━━ NOTES / OBJ ━━━
def add_note(aid,txt,auteur="admin"):
    now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run("INSERT INTO notes_acheteurs (acheteur_id,contenu,date_creation,auteur) VALUES (?,?,?,?)",[aid,txt.strip(),now,auteur])
def get_notes(aid): return query_df("SELECT * FROM notes_acheteurs WHERE acheteur_id=? ORDER BY date_creation DESC",[aid])
def del_note(nid): run("DELETE FROM notes_acheteurs WHERE id=?",[nid])
def get_obj(m):
    df=query_df("SELECT * FROM objectifs WHERE mois=?",[m])
    return df.iloc[0].to_dict() if len(df)>0 else None
def set_obj(m,oca,ocmd):
    if query_val("SELECT id FROM objectifs WHERE mois=?",[m]): run("UPDATE objectifs SET objectif_ca=?,objectif_commandes=? WHERE mois=?",[oca,ocmd,m])
    else: run("INSERT INTO objectifs (mois,objectif_ca,objectif_commandes) VALUES (?,?,?)",[m,oca,ocmd])
def recherche(terme):
    t=f"%{terme}%"
    a=query_df("SELECT 'Acheteur' as type,id,nom as titre,'' as detail FROM acheteurs WHERE nom LIKE ?",[t])
    c=query_df("SELECT 'Commande' as type,c.id,c.boutique as titre,a.nom||' — '||c.montant_total||'€' as detail FROM commandes c JOIN acheteurs a ON c.acheteur_id=a.id WHERE c.boutique LIKE ? OR a.nom LIKE ?",[t,t])
    return pd.concat([a,c],ignore_index=True)
def export_df(df,fmt="csv"):
    if fmt=="csv": return df.to_csv(index=False).encode('utf-8-sig')
    buf=io.BytesIO()
    with pd.ExcelWriter(buf,engine='openpyxl') as w: df.to_excel(w,index=False,sheet_name="Données")
    return buf.getvalue()
def get_fin(df):
    if df.empty: return 0,0
    dav=df[df['statut'].isin(['En cours','Livrée'])]
    nav=(dav['commission_vendeur_eur'].sum()-dav['cout_total'].sum()) if not dav.empty else 0
    rc=df[df['statut']=='Validée']['commission_vendeur_eur'].sum()
    return nav,rc

# ━━━ INIT ━━━
init_db(); inject_css(st.session_state['dark_mode'])

# ━━━ LOGIN ━━━
if not st.session_state['authenticated']:
    _,cc,_=st.columns([1,2,1])
    with cc:
        st.markdown("# ⚡ SalesFlow"); st.caption("Gestion des Ventes"); st.markdown("")
        with st.form("login"):
            u=st.text_input("Identifiant"); p=st.text_input("Mot de passe",type="password")
            if st.form_submit_button("Se connecter",use_container_width=True):
                if auth_check(u,p): st.session_state['authenticated']=True; st.session_state['username']=u; st.rerun()
                else: st.error("Identifiants incorrects.")
        st.caption("Par défaut : `admin` / `admin`")
    st.stop()

# ━━━ SIDEBAR ━━━
np_=cnt_pend()
with st.sidebar:
    st.markdown("### ⚡ SalesFlow"); st.caption(st.session_state['username']); st.markdown("---")
    dark=st.toggle("🌙",value=st.session_state['dark_mode'])
    if dark!=st.session_state['dark_mode']: st.session_state['dark_mode']=dark; st.rerun()
    st.markdown("---")
    pl=f"📩 Demandes ({np_})" if np_>0 else "📩 Demandes"
    menu=st.radio("Nav",[
        "📊 Dashboard",pl,"💰 Coûts","🎯 Objectifs","🔍 Recherche",
        "👤 Acheteurs","🔎 Profil","📋 Commandes","💵 Commissions","⚙️ Paramètres"
    ],label_visibility="collapsed")
    st.markdown("---")
    if st.button("🚪 Déconnexion",use_container_width=True): st.session_state['authenticated']=False; st.rerun()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if menu=="📊 Dashboard":
    ct,cb=st.columns([6,1])
    with ct: st.markdown("# 📊 Dashboard")
    with cb:
        st.markdown("")
        if st.button("➕",key="fab"): st.session_state['show_new_order']=not st.session_state['show_new_order']; st.rerun()
    if np_>0: st.warning(f"📩 **{np_} demande(s) en attente**")
    if st.session_state.get('show_new_order'):
        with st.expander("⚡ Nouvelle commande",expanded=True):
            with st.form("qo",clear_on_submit=True):
                q1,q2=st.columns(2)
                with q1: qa=st.text_input("Acheteur"); qb=st.text_input("Boutique *")
                with q2: qm=st.number_input("Montant (€)",0.0,step=0.5); qt=st.radio("Commission",["En %","Fixe €"],horizontal=True)
                q3,q4=st.columns(2)
                with q3:
                    if qt=="En %": qp=st.number_input("%",0.0,100.0,step=1.0); qe=0.0
                    else: qe=st.number_input("€",0.0,step=0.5); qp=0.0
                with q4: qs=st.selectbox("Statut",["En cours","Validée","Livrée","Annulée"]); qtc=st.selectbox("Technique",["Aucune"]+TECHNIQUES)
                qn=st.text_input("Notes"); tech="" if qtc=="Aucune" else qtc
                c_=calc_cout(tech)
                if c_>0: st.caption(f"💰 Coût: **{c_:.2f} €**")
                if st.form_submit_button("✅",use_container_width=True):
                    if qa.strip() and qb.strip() and qm>0:
                        cv,_,ct_=add_cmd(qa,qb,qm,"pct" if qt=="En %" else "fixe",qp,qe,qn,qs,tech)
                        st.success(f"✅ {cv:.2f} €"); st.session_state['show_new_order']=False; st.rerun()
        st.markdown("---")
    dc=get_cmd(); nav,rc=get_fin(dc)
    ca=dc["montant_total"].sum() if not dc.empty else 0; tc=dc["cout_total"].sum() if not dc.empty else 0
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Acheteurs",len(get_ach())); c2.metric("Commandes",len(dc)); c3.metric("CA",f"{ca:,.2f} €"); c4.metric("Coûts",f"{tc:,.2f} €")
    c5,c6=st.columns(2); c5.metric("💸 Net à venir",f"{nav:,.2f} €"); c6.metric("✅ Reçu",f"{rc:,.2f} €")
    if not dc.empty:
        st.divider(); st.markdown("### Dernières commandes")
        st.dataframe(dc[["date","acheteur","boutique","montant_total","commission_vendeur_eur","technique","cout_total","statut"]].head(10).rename(
            columns={"date":"Date","acheteur":"Acheteur","boutique":"Boutique","montant_total":"Montant","commission_vendeur_eur":"Commission","technique":"Technique","cout_total":"Coût","statut":"Statut"}),use_container_width=True,hide_index=True)

elif menu.startswith("📩"):
    st.markdown("# 📩 Demandes"); ta,th=st.tabs([f"⏳ ({np_})","📜 Historique"])
    with ta:
        dp=get_dem("En attente")
        if dp.empty: st.info("Aucune demande 🎉")
        else:
            for _,d in dp.iterrows():
                st.markdown(f"""<div class="pending-card"><h4>#{d['id']} — {d['nom_client']}</h4><p>🛍️ <b>{d['boutique']}</b> · 💶 <b>{d['montant']:.2f} €</b> · 📅 {d['date_soumission']}</p></div>""",unsafe_allow_html=True)
                if d['notes_client']: st.caption(f"💬 {d['notes_client']}")
                if d['identifiant_boutique'] or d['mdp_boutique']:
                    with st.expander(f"🔐 #{d['id']}"): st.code(f"ID: {d['identifiant_boutique']}\nMDP: {d['mdp_boutique']}")
                with st.expander(f"✅ Valider #{d['id']}"):
                    with st.form(f"v{d['id']}"):
                        v1,v2=st.columns(2)
                        with v1:
                            vt=st.radio("Comm.",["En %","Fixe €"],horizontal=True,key=f"vt{d['id']}")
                            if vt=="En %": vp=st.number_input("%",0.0,100.0,step=1.0,key=f"vp{d['id']}"); ve=0.0
                            else: ve=st.number_input("€",0.0,step=0.5,key=f"ve{d['id']}"); vp=0.0
                        with v2: vtc=st.selectbox("Technique",["Aucune"]+TECHNIQUES,key=f"vtc{d['id']}")
                        vn=st.text_input("Notes",key=f"vn{d['id']}")
                        if st.form_submit_button("✅",use_container_width=True):
                            tech="" if vtc=="Aucune" else vtc
                            cv,_,_=add_cmd(d['nom_client'],d['boutique'],d['montant'],"pct" if vt=="En %" else "fixe",vp,ve,
                                f"{d['notes_client']} | {vn}".strip(" | "),"En cours",tech,ident=d['identifiant_boutique'],mdp=d['mdp_boutique'])
                            val_dem(int(d['id'])); st.success(f"✅ {cv:.2f} €"); st.rerun()
                if st.button(f"❌ #{d['id']}",key=f"r{d['id']}"): rej_dem(int(d['id'])); st.rerun()
                st.markdown("---")
    with th:
        dh=get_dem(); dh=dh[dh['statut']!="En attente"]
        if not dh.empty: st.dataframe(dh[['id','date_soumission','nom_client','boutique','montant','statut']].rename(columns={'id':'ID','date_soumission':'Date','nom_client':'Client','boutique':'Boutique','montant':'Montant','statut':'Statut'}),use_container_width=True,hide_index=True)

elif menu=="💰 Coûts":
    st.markdown("# 💰 Coûts"); st.caption("Prix définis une fois, appliqués automatiquement.")
    dcc=get_couts()
    if not dcc.empty:
        for _,r in dcc.iterrows():
            c1,c2,c3=st.columns([2,2,1])
            with c1: st.markdown(f"**{r['nom']}**")
            with c2: st.markdown(f"`{r['prix']:.2f} €`")
            with c3:
                if st.button("🗑️",key=f"dc{r['nom']}"): del_cout(r['nom']); st.rerun()
    st.divider()
    with st.form("fc",clear_on_submit=True):
        f1,f2=st.columns(2)
        with f1: cn=st.selectbox("Technique",TECHNIQUES)
        with f2: cp=st.number_input("Prix (€)",0.0,step=0.5)
        if st.form_submit_button("💾",use_container_width=True):
            if cp>0: set_cout(cn,cp); st.success(f"**{cn}** → {cp:.2f} €"); st.rerun()

elif menu=="🎯 Objectifs":
    st.markdown("# 🎯 Objectifs")
    with st.form("fo"):
        m=st.text_input("Mois",value=datetime.now().strftime("%Y-%m"))
        o1,o2=st.columns(2)
        with o1: oca=st.number_input("CA (€)",0.0,step=100.0)
        with o2: ocmd=st.number_input("Commandes",0,step=1)
        if st.form_submit_button("💾",use_container_width=True): set_obj(m,oca,ocmd); st.success("OK"); st.rerun()

elif menu=="🔍 Recherche":
    st.markdown("# 🔍 Recherche"); t=st.text_input("🔎",placeholder="Nom, boutique...")
    if t and len(t)>=2:
        res=recherche(t)
        if res.empty: st.warning("Rien.")
        else:
            for tr in res['type'].unique():
                st.markdown(f"### {tr}s")
                for _,r in res[res['type']==tr].iterrows(): st.markdown(f"**{r['titre']}** {r['detail']}")

elif menu=="👤 Acheteurs":
    st.markdown("# 👤 Acheteurs"); ta,tl=st.tabs(["➕","📋"])
    with ta:
        with st.form("fa",clear_on_submit=True):
            c1,c2=st.columns(2)
            with c1: nom=st.text_input("Nom *"); parr=st.text_input("Parrain")
            with c2: cp=st.number_input("Comm. (%)",0.0,100.0,step=1.0); ib=st.text_input("ID boutique"); mb=st.text_input("MDP boutique",type="password")
            if st.form_submit_button("✅",use_container_width=True):
                if nom.strip():
                    ok,msg=add_ach(nom,parr,cp,ib,mb)
                    if ok: st.success(f"**{nom}** ajouté !"); st.rerun()
                    else: st.error(msg)
    with tl:
        dfa=get_ach()
        if not dfa.empty: st.dataframe(dfa[['nom','parrain','commission_parrain','date_creation']].rename(columns={'nom':'Nom','parrain':'Parrain','commission_parrain':'Comm. (%)','date_creation':'Inscrit'}),use_container_width=True,hide_index=True)

elif menu=="🔎 Profil":
    st.markdown("# 🔎 Profil"); dfa=get_ach()
    if dfa.empty: st.warning("Aucun.")
    else:
        an=st.selectbox("Acheteur",dfa['nom'].tolist()); ar=dfa[dfa['nom']==an].iloc[0]; aid=int(ar['id'])
        badge=f'<span class="badge">Parrain : {ar["parrain"]} ({ar["commission_parrain"]}%)</span>' if ar['parrain']!="Aucun" else '<span class="badge">Pas de parrain</span>'
        st.markdown(f'<div class="profil-card"><h3>👤 {ar["nom"]}</h3><p>📅 {ar["date_creation"]}</p>{badge}</div>',unsafe_allow_html=True)
        if ar['identifiant_boutique'] or ar['mdp_boutique']:
            st.markdown("### 🔐 Accès"); st.markdown(f'<div class="cred-box">ID: {ar["identifiant_boutique"] or "—"}\nMDP: {ar["mdp_boutique"] or "—"}</div>',unsafe_allow_html=True)
        dh=get_cmd(aid)
        if not dh.empty:
            nav,rc=get_fin(dh)
            st.markdown(f'<div class="kpi-row"><div class="kpi-mini"><div class="value">{len(dh)}</div><div class="label">Commandes</div></div><div class="kpi-mini"><div class="value">{dh["montant_total"].sum():,.2f} €</div><div class="label">Total</div></div><div class="kpi-mini"><div class="value">{nav:,.2f} €</div><div class="label">Net à venir</div></div><div class="kpi-mini"><div class="value">{rc:,.2f} €</div><div class="label">Reçu</div></div></div>',unsafe_allow_html=True)
            st.dataframe(dh[['date','boutique','montant_total','commission_vendeur_eur','technique','cout_total','statut']].rename(columns={'date':'Date','boutique':'Boutique','montant_total':'Montant','commission_vendeur_eur':'Commission','technique':'Technique','cout_total':'Coût','statut':'Statut'}),use_container_width=True,hide_index=True)
        st.divider(); st.markdown("### 💬 Notes")
        with st.form("fn",clear_on_submit=True):
            nt=st.text_area("Note")
            if st.form_submit_button("💬",use_container_width=True):
                if nt.strip(): add_note(aid,nt,st.session_state['username']); st.rerun()
        for _,n in get_notes(aid).iterrows(): st.markdown(f'<div class="note-bubble"><div class="note-date">{n["auteur"]} — {n["date_creation"]}</div>{n["contenu"]}</div>',unsafe_allow_html=True)
        with st.expander("✏️ Modifier"):
            with st.form("fe"):
                c1,c2=st.columns(2)
                with c1: nn=st.text_input("Nom",value=ar['nom']); np=st.text_input("Parrain",value=ar['parrain'] if ar['parrain']!="Aucun" else ""); nco=st.number_input("Comm.",value=float(ar['commission_parrain']),min_value=0.0,max_value=100.0)
                with c2: ni=st.text_input("ID boutique",value=ar['identifiant_boutique']); nm=st.text_input("MDP",value=ar['mdp_boutique'],type="password")
                if st.form_submit_button("💾",use_container_width=True):
                    ok,_=mod_ach(aid,nn,np,nco,ni,nm)
                    if ok: st.success("OK"); st.rerun()

elif menu=="📋 Commandes":
    ct,cb=st.columns([5,1])
    with ct: st.markdown("# 📋 Commandes")
    with cb:
        st.markdown("")
        if st.button("➕",key="nc"): st.session_state['show_new_order_page']=not st.session_state.get('show_new_order_page',False); st.rerun()
    if st.session_state.get('show_new_order_page'):
        with st.expander("⚡ Nouvelle",expanded=True):
            with st.form("fcmd",clear_on_submit=True):
                p1,p2=st.columns(2)
                with p1: pa=st.text_input("Acheteur"); pb=st.text_input("Boutique *"); pm=st.number_input("Montant",0.0,step=0.5)
                with p2:
                    pt=st.radio("Comm.",["En %","Fixe €"],horizontal=True)
                    if pt=="En %": pp=st.number_input("%",0.0,100.0,step=1.0); pe=0.0
                    else: pe=st.number_input("€",0.0,step=0.5); pp=0.0
                    ps=st.selectbox("Statut",["En cours","Validée","Livrée","Annulée"]); ptc=st.selectbox("Technique",["Aucune"]+TECHNIQUES)
                pn=st.text_input("Notes"); tech="" if ptc=="Aucune" else ptc
                if st.form_submit_button("✅",use_container_width=True):
                    if pa.strip() and pb.strip() and pm>0:
                        cv,_,_=add_cmd(pa,pb,pm,"pct" if pt=="En %" else "fixe",pp,pe,pn,ps,tech)
                        st.success(f"✅ {cv:.2f} €"); st.session_state['show_new_order_page']=False; st.rerun()
        st.markdown("---")
    dc=get_cmd()
    if dc.empty: st.info("Aucune.")
    else:
        cf1,cf2,cf3=st.columns(3)
        with cf1: fa=st.multiselect("Acheteur",dc['acheteur'].unique().tolist())
        with cf2: fb=st.multiselect("Boutique",dc['boutique'].unique().tolist())
        with cf3: fs=st.multiselect("Statut",dc['statut'].unique().tolist())
        df=dc.copy()
        if fa: df=df[df['acheteur'].isin(fa)]
        if fb: df=df[df['boutique'].isin(fb)]
        if fs: df=df[df['statut'].isin(fs)]
        nav,rc=get_fin(df)
        s1,s2,s3=st.columns(3); s1.metric("💸 Net à venir",f"{nav:,.2f} €"); s2.metric("✅ Reçu",f"{rc:,.2f} €"); s3.metric("Coûts",f"{df['cout_total'].sum():,.2f} €")
        dcols=['id','date','acheteur','boutique','montant_total','commission_vendeur_eur','technique','cout_total','statut','notes']
        rm={'id':'ID','date':'Date','acheteur':'Acheteur','boutique':'Boutique','montant_total':'Montant','commission_vendeur_eur':'Commission','technique':'Technique','cout_total':'Coût','statut':'Statut','notes':'Notes'}
        st.dataframe(df[dcols].rename(columns=rm),use_container_width=True,hide_index=True)
        e1,e2=st.columns(2)
        with e1: st.download_button("CSV",export_df(df[dcols].rename(columns=rm),"csv"),"cmd.csv","text/csv",use_container_width=True)
        with e2: st.download_button("Excel",export_df(df[dcols].rename(columns=rm),"xlsx"),"cmd.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",use_container_width=True)
        st.divider(); st.markdown("### ✏️ Modifier")
        eid=st.number_input("ID",min_value=1,step=1,key="eid")
        if eid in dc['id'].values:
            cr=dc[dc['id']==eid].iloc[0]
            with st.form("fedit"):
                e1,e2=st.columns(2)
                with e1: eb=st.text_input("Boutique",value=cr['boutique']); em=st.number_input("Montant",value=float(cr['montant_total']),step=0.5)
                with e2:
                    et=st.radio("Comm.",["En %","Fixe €"],horizontal=True,index=0 if cr['commission_mode']=='pct' else 1)
                    if et=="En %": epp=st.number_input("%",value=float(cr['commission_vendeur_pct']),step=1.0); eee=0.0
                    else: eee=st.number_input("€",value=float(cr['commission_vendeur_eur']),step=0.5); epp=0.0
                    es=st.selectbox("Statut",["En cours","Validée","Livrée","Annulée"],index=["En cours","Validée","Livrée","Annulée"].index(cr['statut']))
                    ct_=cr['technique'] if cr['technique'] else "Aucune"
                    etc=st.selectbox("Technique",["Aucune"]+TECHNIQUES,index=(TECHNIQUES.index(ct_)+1) if ct_ in TECHNIQUES else 0)
                    en=st.text_input("Notes",value=cr['notes'])
                if st.form_submit_button("💾",use_container_width=True):
                    mod_cmd(int(eid),eb,em,"pct" if et=="En %" else "fixe",epp,eee,en,es,"" if etc=="Aucune" else etc)
                    st.success("OK"); st.rerun()
        st.divider()
        did=st.number_input("Supprimer",min_value=1,step=1,key="did")
        if st.button("🗑️",key="bd"):
            if did in dc['id'].values: del_cmd(int(did)); st.rerun()

elif menu=="💵 Commissions":
    st.markdown("# 💵 Commissions"); dc=get_cmd()
    if dc.empty: st.info("Aucune.")
    else:
        nav,rc=get_fin(dc)
        c1,c2,c3=st.columns(3); c1.metric("💸 Net à venir",f"{nav:,.2f} €"); c2.metric("✅ Reçu",f"{rc:,.2f} €"); c3.metric("Coûts",f"{dc['cout_total'].sum():,.2f} €")
        t1,t2=st.tabs(["Parrains","Boutiques"])
        with t1:
            dp=dc[dc['parrain']!="Aucun"]
            if not dp.empty:
                rec=dp.groupby('parrain').agg(Filleuls=('acheteur','nunique'),CA=('montant_total','sum'),Comm=('commission_parrain_eur','sum')).reset_index().rename(columns={'parrain':'Parrain'})
                st.dataframe(rec,use_container_width=True,hide_index=True)
        with t2:
            rb=dc.groupby('boutique').agg(CA=('montant_total','sum'),Comm=('commission_vendeur_eur','sum'),Coûts=('cout_total','sum')).reset_index()
            rb['Profit']=rb['Comm']-rb['Coûts']; rb=rb.rename(columns={'boutique':'Boutique'})
            st.dataframe(rb,use_container_width=True,hide_index=True)

elif menu=="⚙️ Paramètres":
    st.markdown("# ⚙️ Paramètres")
    with st.form("fpw"):
        op=st.text_input("Actuel",type="password"); n1=st.text_input("Nouveau",type="password"); n2=st.text_input("Confirmer",type="password")
        if st.form_submit_button("🔐",use_container_width=True):
            if not auth_check(st.session_state['username'],op): st.error("Incorrect.")
            elif n1!=n2: st.error("Pas identiques.")
            elif len(n1)<4: st.error("Min 4 car.")
            else: change_pw(st.session_state['username'],n1); st.success("OK")
    st.markdown("---"); st.caption("⚡ SalesFlow v6 — Turso Cloud · Données sauvegardées en ligne")
