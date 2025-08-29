import streamlit as st
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random

st.title("📝 Assistente de Escrita Acadêmica")
st.write("Detecta plágio semântico e sugere melhorias")

# Base de conhecimento simulada (textos "conhecidos")
BASE_TEXTOS = {
    "machine_learning": [
        "Machine learning é um subcampo da inteligência artificial que permite aos computadores aprender sem serem explicitamente programados.",
        "Os algoritmos de aprendizado de máquina constroem um modelo baseado em dados de treinamento para fazer predições ou decisões.",
        "Deep learning utiliza redes neurais artificiais com múltiplas camadas para modelar e entender dados complexos.",
        "O processamento de linguagem natural combina linguística computacional com modelos estatísticos e de aprendizado de máquina."
    ],
    "inteligencia_artificial": [
        "Inteligência artificial refere-se à capacidade das máquinas de realizar tarefas que normalmente requerem inteligência humana.",
        "IA pode ser classificada como estreita ou geral, sendo que a IA geral ainda não foi alcançada.",
        "Algoritmos de IA são usados em reconhecimento de imagem, processamento de fala e tomada de decisões automatizada.",
        "A ética em IA tornou-se uma preocupação importante devido ao potencial impacto social dessas tecnologias."
    ],
    "programacao": [
        "Python é uma linguagem de programação de alto nível conhecida por sua sintaxe clara e legível.",
        "Estruturas de dados são formas de organizar e armazenar dados de maneira eficiente em programas de computador.",
        "Algoritmos são sequências de instruções bem definidas para resolver problemas computacionais específicos.",
        "A programação orientada a objetos organiza código em classes e objetos para melhor modularidade."
    ]
}

def preparar_base_conhecimento():
    """Prepara base de textos conhecidos"""
    todos_textos = []
    for categoria, textos in BASE_TEXTOS.items():
        todos_textos.extend(textos)
    return todos_textos

def dividir_em_sentencas(texto):
    """Divide texto em sentenças"""
    # Regex simples para dividir sentenças
    sentencas = re.split(r'[.!?]+', texto)
    # Remove sentenças muito curtas
    sentencas = [s.strip() for s in sentencas if len(s.strip()) > 20]
    return sentencas

def calcular_similaridade(texto_usuario, base_textos):
    """Calcula similaridade usando TF-IDF"""
    # Combina texto do usuário com base
    todos_textos = [texto_usuario] + base_textos
    
    # TF-IDF
    vectorizer = TfidfVectorizer(
        stop_words=None,  # Mantém simples
        ngram_range=(1, 2),  # Uni e bigramas
        max_features=1000
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(todos_textos)
        
        # Similaridade do texto do usuário com cada texto da base
        similaridades = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        
        return similaridades
    except:
        # Se der erro, retorna similaridades baixas
        return np.zeros(len(base_textos))

def detectar_plagio(sentencas_usuario, base_textos, threshold=0.3):
    """Detecta possível plágio em cada sentença"""
    resultados = []
    
    for i, sentenca in enumerate(sentencas_usuario):
        similaridades = calcular_similaridade(sentenca, base_textos)
        max_sim = np.max(similaridades)
        idx_similar = np.argmax(similaridades)
        
        status = "ok"
        if max_sim > 0.6:
            status = "alto_risco"
        elif max_sim > threshold:
            status = "suspeito"
        
        resultados.append({
            'sentenca': sentenca,
            'similaridade_maxima': max_sim,
            'texto_similar': base_textos[idx_similar] if len(base_textos) > idx_similar else "",
            'status': status,
            'posicao': i
        })
    
    return resultados

def sugerir_reescrita(sentenca):
    """Sugere reescritas simples"""
    sugestoes = []
    
    # Regras simples de reescrita
    regras = [
        # Voz passiva para ativa
        (r'é (usado|utilizado|empregado)', r'usa-se'),
        (r'são (usados|utilizados|empregados)', r'usam-se'),
        
        # Sinônimos comuns
        (r'utilizar', r'usar'),
        (r'realizar', r'fazer'),
        (r'desenvolver', r'criar'),
        (r'implementar', r'aplicar'),
        
        # Estruturas alternativas
        (r'é possível', r'pode-se'),
        (r'é importante', r'cabe destacar'),
        (r'é necessário', r'deve-se'),
    ]
    
    texto_reescrito = sentenca
    mudancas_feitas = []
    
    for padrao, substituto in regras:
        if re.search(padrao, texto_reescrito, re.IGNORECASE):
            texto_reescrito = re.sub(padrao, substituto, texto_reescrito, flags=re.IGNORECASE)
            mudancas_feitas.append(f"'{padrao}' → '{substituto}'")
    
    if mudancas_feitas:
        sugestoes.append({
            'tipo': 'Substituição de termos',
            'original': sentenca,
            'sugestao': texto_reescrito,
            'mudancas': mudancas_feitas
        })
    
    # Sugestão de paráfrase simples
    if len(sentenca.split()) > 10:
        sugestoes.append({
            'tipo': 'Reestruturação',
            'original': sentenca,
            'sugestao': f"Em outras palavras, {sentenca.lower()}",
            'mudancas': ['Adição de conectivo explicativo']
        })
    
    return sugestoes

# Interface principal
st.subheader("📄 Cole seu texto acadêmico")

texto_usuario = st.text_area(
    "Texto para análise:",
    placeholder="Cole aqui o texto que deseja verificar...",
    height=200
)

col1, col2 = st.columns([1, 3])

with col1:
    analisar_btn = st.button("🔍 Analisar", type="primary")

with col2:
    threshold = st.slider("Sensibilidade", 0.1, 0.8, 0.3, 0.1, 
                         help="Quão similar precisa ser para considerar suspeito")

if analisar_btn and texto_usuario.strip():
    
    st.write("---")
    st.subheader("📊 Resultado da Análise")
    
    # Preparar dados
    base_textos = preparar_base_conhecimento()
    sentencas = dividir_em_sentencas(texto_usuario)
    
    if not sentencas:
        st.warning("⚠️ Texto muito curto ou sem sentenças válidas")
    else:
        # Análise de plágio
        with st.spinner("Analisando similaridades semânticas..."):
            resultados = detectar_plagio(sentencas, base_textos, threshold)
        
        # Estatísticas gerais
        total_sentencas = len(resultados)
        alto_risco = len([r for r in resultados if r['status'] == 'alto_risco'])
        suspeito = len([r for r in resultados if r['status'] == 'suspeito'])
        ok = len([r for r in resultados if r['status'] == 'ok'])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total de sentenças", total_sentencas)
        with col2:
            st.metric("Alto risco", alto_risco, delta=f"{alto_risco/total_sentencas*100:.1f}%")
        with col3:
            st.metric("Suspeitas", suspeito, delta=f"{suspeito/total_sentencas*100:.1f}%")
        with col4:
            st.metric("OK", ok, delta=f"{ok/total_sentencas*100:.1f}%")
        
        # Análise detalhada
        st.write("### 🔍 Análise Detalhada")
        
        for resultado in resultados:
            
            if resultado['status'] == 'alto_risco':
                cor = '🔴'
                tipo = 'ALTO RISCO'
                color = 'red'
            elif resultado['status'] == 'suspeito':
                cor = '🟡'
                tipo = 'SUSPEITO'
                color = 'orange'
            else:
                cor = '🟢'
                tipo = 'OK'
                color = 'green'
            
            with st.expander(f"{cor} Sentença {resultado['posicao']+1} - {tipo} ({resultado['similaridade_maxima']:.1%})"):
                
                st.markdown(f"**Texto analisado:**")
                st.write(f"_{resultado['sentenca']}_")
                
                if resultado['status'] != 'ok':
                    st.markdown(f"**Texto similar encontrado:**")
                    st.write(f"_{resultado['texto_similar']}_")
                    
                    st.markdown(f"**Similaridade:** {resultado['similaridade_maxima']:.1%}")
                    
                    # Sugestões de reescrita
                    if resultado['status'] == 'alto_risco':
                        st.write("**💡 Sugestões de Reescrita:**")
                        sugestoes = sugerir_reescrita(resultado['sentenca'])
                        
                        for sugestao in sugestoes:
                            st.write(f"**{sugestao['tipo']}:**")
                            st.write(f"🔄 _{sugestao['sugestao']}_")
                            if sugestao['mudancas']:
                                st.write(f"Mudanças: {', '.join(sugestao['mudancas'])}")
                            st.write("---")

elif analisar_btn:
    st.warning("⚠️ Por favor, cole um texto para análise")

# Informações e exemplos
if not analisar_btn or not texto_usuario.strip():
    st.write("---")
    st.subheader("ℹ️ Como funciona")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🔍 Detecção Semântica**")
        st.write("• Usa TF-IDF + Cosine Similarity")
        st.write("• Detecta paráfrases, não só cópias")
        st.write("• Analisa sentença por sentença")
    
    with col2:
        st.write("**💡 Sugestões Inteligentes**")
        st.write("• Substituição de termos")
        st.write("• Reestruturação de frases")
        st.write("• Alternativas de escrita")
    
    st.write("**🎯 Diferencial:** Vai além do Ctrl+C/Ctrl+V - detecta ideias muito similares!")
    
    st.subheader("🧪 Teste com este exemplo:")
    
    exemplo = """
    Machine learning é um subcampo da inteligência artificial que permite que computadores aprendam sem programação explícita.
    Os algoritmos de ML constroem modelos baseados em dados de treino para fazer predições.
    Deep learning usa redes neurais com várias camadas para modelar dados complexos.
    """
    
    if st.button("📋 Usar exemplo"):
        st.experimental_rerun()

st.write("---")
st.caption("⚡ Desenvolvido para auxiliar na escrita acadêmica ética")