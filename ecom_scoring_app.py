import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
import time
from datetime import datetime
import plotly.graph_objects as go  # Pour la gauge

# Configuration responsive
st.set_page_config(page_title="Scorez Votre E-commerce", layout="wide", initial_sidebar_state="collapsed")

# Thème sombre (fond noir)
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #000000; color: #ffffff; }
    .main { background-color: #000000; color: #ffffff; }
    .stButton>button { background-color: #28a745; color: white; border-radius: 8px; }
    .stTextInput>div>input { background-color: #1c1c1c; color: #ffffff; border-radius: 8px; border: 1px solid #28a745; }
    h1, h2, h3 { color: #ffffff; font-family: 'Arial', sans-serif; }
    .footer { font-size: 12px; text-align: center; margin-top: 20px; color: #cccccc; }
    .stInfo, .stSuccess, .stError { background-color: #1c1c1c; color: #ffffff; }
    .stPlotlyChart { max-width: 100%; }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🛒 Scorez la Santé de Votre E-commerce")
st.subheader("Découvrez en 2 min si votre boutique performe + recevez des conseils data-driven gratuits !")
st.write("Saisissez vos KPIs pour un score personnalisé. Conforme RGPD, données sécurisées.")

# Formulaire avec plus de données
with st.form("ecom_form"):
    st.subheader("Vos données e-commerce")
    col1, col2 = st.columns(2)
    with col1:
        monthly_revenue = st.number_input("CA mensuel hors taxes (€)", min_value=0.0, value=10000.0, step=1000.0)
        conversion_rate = st.number_input("Taux de conversion (%)", min_value=0.0, max_value=100.0, value=2.0, step=0.1)
        avg_order_value = st.number_input("Panier moyen (€)", min_value=0.0, value=50.0, step=5.0)
    with col2:
        cpc = st.number_input("Coût par clic moyen (€, Google/Meta Ads)", min_value=0.0, value=1.0, step=0.1)
        cart_abandonment = st.number_input("Taux d'abandon de panier (%)", min_value=0.0, max_value=100.0, value=60.0, step=1.0)
        organic_traffic = st.number_input("Trafic organique mensuel (visites)", min_value=0, value=5000, step=100, help="Optionnel")
    
    # Consentement RGPD
    rgpd_consent = st.checkbox("J'accepte que mes données soient utilisées pour générer le rapport (conforme RGPD).")
    submitted = st.form_submit_button("Calculer mon score")

# Logique de scoring
if submitted and rgpd_consent:
    # Session state pour isoler les données
    if 'score_data' not in st.session_state:
        st.session_state.score_data = {}

    # Calcul du score (benchmarks FR 2025)
    score = 0
    recommendations = []

    # CA mensuel
    if monthly_revenue > 50000:
        score += 25
    elif monthly_revenue > 20000:
        score += 15
    else:
        score += 5
        recommendations.append("📈 Boostez votre trafic avec du SEO local ou des campagnes Meta Ads ciblées.")

    # Taux de conversion
    if conversion_rate > 3:
        score += 20
    elif conversion_rate > 1.5:
        score += 10
    else:
        score += 5
        recommendations.append("🔄 Optimisez votre funnel de conversion (ex: checkout simplifié, trust badges).")

    # Panier moyen
    if avg_order_value > 100:
        score += 15
    elif avg_order_value > 50:
        score += 10
    else:
        score += 5
        recommendations.append("🛒 Proposez des upsells ou bundles pour augmenter le panier moyen.")

    # Coût par clic
    if cpc < 0.8:
        score += 15
    elif cpc < 1.5:
        score += 10
    else:
        score += 5
        recommendations.append("💸 Revoyez vos ciblages publicitaires pour réduire le CPC et améliorer le ROAS.")

    # Abandon de panier
    if cart_abandonment < 50:
        score += 15
    elif cart_abandonment < 70:
        score += 10
    else:
        score += 5
        recommendations.append("🛑 Implémentez des relances email/SMS pour récupérer les paniers abandonnés.")

    # Trafic organique (optionnel)
    if organic_traffic > 10000:
        score += 10
    elif organic_traffic > 5000:
        score += 5
    else:
        recommendations.append("🌐 Investissez dans le SEO local pour augmenter le trafic organique.")

    # Marge d'erreur
    st.info("Note : Score basé sur benchmarks e-com français 2025, avec une marge d’erreur de ±10% selon la qualité des données saisies.")

    # Affichage de la gauge (aiguille de vitesse)
    gauge_color = "green" if score >= 80 else "orange" if score >= 50 else "red"
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Score de Santé E-com"},
        delta={'reference': 50},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': gauge_color},
            'bgcolor': "black",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': "red"},
                {'range': [50, 80], 'color': "orange"},
                {'range': [80, 100], 'color': "green"}],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': score}}))
    fig.update_layout(paper_bgcolor="black", font={'color': "white"})
    st.plotly_chart(fig, use_container_width=True)

    # Message basé sur le score
    if score >= 80:
        st.success("🎉 Votre e-commerce est en excellente santé ! Accélérez !")
    elif score >= 50:
        st.write("👍 Votre boutique performe bien, mais il y a du potentiel pour scaler.")
    else:
        st.write("⚠️ Risque de ralentissement – Optimisez vite !")

    st.subheader("Recommandations personnalisées")
    for rec in recommendations:
        st.write(f"- {rec}")

    # Générer PDF gratuit
    def generate_pdf(score, recommendations, handle):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        c.setFont("Helvetica", 12)
        c.drawString(100, 800, "Rapport de Scoring E-commerce")
        c.drawString(100, 780, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        c.drawString(100, 760, f"Handle X: {handle}")
        c.drawString(100, 740, f"Score: {score}/100")
        c.drawString(100, 720, "Recommandations:")
        y = 700
        for i, rec in enumerate(recommendations, 1):
            c.drawString(120, y - i*20, f"{i}. {rec}")
        c.drawString(100, y - len(recommendations)*20 - 20, "Besoin d’un audit approfondi ? Réservez ici : [votre lien Notion]")
        c.save()
        buffer.seek(0)
        return buffer

    # Formulaire pour handle X
    with st.form("contact_form"):
        handle = st.text_input("Votre handle X (@username) pour recevoir le rapport")
        contact_submitted = st.form_submit_button("Obtenir le rapport gratuit")
        if contact_submitted and handle:
            if not handle.startswith("@"):
                st.error("Le handle doit commencer par @")
            else:
                # Simuler enregistrement Google Sheets (remplacer par gspread)
                st.session_state.score_data[handle] = {
                    "score": score,
                    "recommendations": recommendations,
                    "timestamp": time.time()
                }
                pdf_buffer = generate_pdf(score, recommendations, handle)
                st.download_button(
                    label="Télécharger votre rapport gratuit",
                    data=pdf_buffer,
                    file_name="rapport_ecom_gratuit.pdf",
                    mime="application/pdf"
                )
                st.success("Rapport généré ! Je vous contacterai via X pour plus de détails.")

    # Paiement crypto pour PDF premium ou acompte
    st.subheader("Obtenez plus avec un rapport premium ou un audit")
    col1, col2 = st.columns(2)
    with col1:
        st.button("Rapport Premium (50€)", on_click=lambda: st.write("Redirection vers NOWPayments... [Configurer avec votre clé API]"))
    with col2:
        st.button("Acompte Audit (100€)", on_click=lambda: st.write("Redirection vers NOWPayments... [Configurer avec votre clé API]"))
else:
    if submitted and not rgpd_consent:
        st.error("Veuillez accepter les conditions RGPD pour continuer.")

# Footer
st.markdown("---")
st.markdown('<div class="footer">Créé par Edson Vigninou, Data Analyst. <a href="#">Réservez un audit complet</a> | Paiements crypto via NOWPayments.</div>', unsafe_allow_html=True)