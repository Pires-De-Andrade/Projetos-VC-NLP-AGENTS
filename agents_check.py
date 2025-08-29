import streamlit as st
import requests
import json
import re
from datetime import datetime

st.title("🔍 Verificador de Fatos com Agentes")
st.write("Um experimento com múltiplos agentes para fact-checking")

# Input da afirmação
claim = st.text_input("Que afirmação você quer verificar?", 
                     placeholder="Ex: Python foi criado em 1991")

if st.button("Verificar") and claim:
    
    # AGENTE 1: BUSCADOR
    st.write("---")
    st.write("**🔍 AGENTE 1 - BUSCADOR**")
    
    # Extrair palavras-chave básicas
    keywords = []
    words = claim.split()
    for word in words:
        if len(word) > 3 and word.isalpha():
            keywords.append(word)
    
    st.write(f"Palavras-chave encontradas: {', '.join(keywords[:3])}")
    
    # Buscar no Wikipedia
    sources = []
    for keyword in keywords[:2]: 
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{keyword}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                sources.append({
                    'titulo': data.get('title', ''),
                    'texto': data.get('extract', ''),
                    'link': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                    'keyword': keyword
                })
                st.write(f"✅ Encontrei algo sobre: {keyword}")
            else:
                st.write(f"❌ Nada encontrado para: {keyword}")
        except:
            st.write(f"⚠️ Erro buscando: {keyword}")
    
    # AGENTE 2: ANALISADOR  
    st.write("**📊 AGENTE 2 - ANALISADOR**")
    
    analyzed = []  
    
    if not sources:
        st.write("❌ Sem fontes para analisar")
    else:
        for source in sources:
            # Análise bem básica de relevância
            claim_words = set(claim.lower().split())
            source_words = set(source['texto'].lower().split())
            overlap = len(claim_words.intersection(source_words))
            
            relevance = overlap / len(claim_words) if claim_words else 0
            
            # Credibilidade simples (Wikipedia = 0.8)
            credibility = 0.8
            
            analyzed.append({
                **source,
                'relevancia': relevance,
                'credibilidade': credibility,
                'score': relevance * credibility
            })
            
            st.write(f"📄 {source['titulo']}: Relevância {relevance:.2f}, Score final {relevance * credibility:.2f}")
    
    # AGENTE 3: SINTETIZADOR
    st.write("**⚖️ AGENTE 3 - SINTETIZADOR**") 
    
    if analyzed==True:
        # Pega a melhor fonte
        best_source = max(analyzed, key=lambda x: x['score'])
        avg_score = sum(s['score'] for s in analyzed) / len(analyzed)
        
        # Veredito bem simples
        if avg_score > 0.3:
            verdict = "PROVÁVEL"
            cor = "green"
        elif avg_score > 0.1:
            verdict = "INCERTO" 
            cor = "orange"
        else:
            verdict = "IMPROVÁVEL"
            cor = "red"
        
        st.markdown(f"### Resultado: <span style='color:{cor}'>{verdict}</span>", unsafe_allow_html=True)
        st.write(f"Score médio: {avg_score:.3f}")
        
        # Melhor evidência
        st.write("**Melhor evidência encontrada:**")
        st.write(f"📚 Fonte: {best_source['titulo']}")
        
        # Pega apenas as primeiras 2 frases relevantes
        sentences = best_source['texto'].split('.')[:2]
        for sentence in sentences:
            if any(word.lower() in sentence.lower() for word in claim.split()):
                st.write(f"💡 {sentence.strip()}")
        
        if best_source['link']:
            st.write(f"🔗 [Ver fonte completa]({best_source['link']})")
        
        # Debug info (mostra que você entende o que está fazendo)
        with st.expander("🔧 Debug - Ver detalhes"):
            st.json({
                'afirmacao_original': claim,
                'palavras_chave': keywords[:3],
                'num_fontes': len(sources),
                'scores': [s['score'] for s in analyzed],
                'melhor_fonte': best_source['titulo']
            })
    
    else:
        st.write("❌ Não consegui encontrar informações suficientes para verificar")
        st.write("Tente reformular a afirmação ou usar termos mais específicos")

# Seção de exemplo
st.write("---")
st.write("**💡 Dicas de teste:**")
st.write("- 'Python foi criado por Guido van Rossum'")
st.write("- 'Einstein nasceu na Alemanha'") 
st.write("- 'Tesla foi fundada em 2003'")

st.write("**⚠️ Limitações atuais:**")
st.write("- Só busca no Wikipedia (em inglês)")
st.write("- Análise de relevância muito básica") 
st.write("- Não detecta informações conflitantes ainda")