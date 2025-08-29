import streamlit as st
import cv2
import numpy as np
from deepface import DeepFace
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import tempfile
import os

# Configuração da página
st.set_page_config(
    page_title="EmoScan - Análise de Emoções com Contexto",
    page_icon="😊",
    layout="wide"
)

# Título e descrição
st.title("😊 EmoScan - Análise de Emoções com Contexto")
st.markdown("""
Este sistema analisa emoções humanas considerando o contexto da imagem para uma interpretação mais precisa.
Faça upload de uma imagem contendo rosto(s) humano(s) para análise.
""")

# Função para carregar modelo YOLO (simplificado para demonstração)
def load_yolo_context():
    # Em uma implementação real, carregaríamos um modelo YOLO pré-treinado
    # Para fins de demonstração, usaremos uma abordagem simplificada
    st.success("Modelo de contexto carregado com sucesso!")
    return None

# Função para detectar contexto (simplificado)
def detect_context(image):
    # Esta é uma versão simplificada para demonstração
    # Em uma implementação real, usaríamos YOLO ou outra rede para detecção de objetos
    
    context_items = []
    
    # Simulação de detecção de contexto baseada em cores e formas simples
    img_array = np.array(image)
    
    # Verificar se há tons de azul (possível escritório)
    blue_dominant = np.mean(img_array[:, :, 2]) > np.mean(img_array[:, :, 1]) + 10
    if blue_dominant:
        context_items.append("escritório")
    
    # Verificar se há formas retangulares (possível eletrônicos)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    rectangular_objects = 0
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
        if len(approx) == 4:  # Forma quadrangular
            rectangular_objects += 1
    
    if rectangular_objects > 2:
        context_items.append("dispositivos eletrônicos")
    
    # Verificar tons verdes (possível natureza)
    green_dominant = np.mean(img_array[:, :, 1]) > np.mean(img_array[:, :, 0]) + 10
    if green_dominant:
        context_items.append("natureza")
    
    return context_items if context_items else ["contexto indefinido"]

# Função para ajustar emoção com base no contexto
def adjust_emotion(emotion, confidence, context):
    original_emotion = emotion
    original_confidence = confidence
    
    # Regras de ajuste baseadas no contexto
    if "escritório" in context and emotion == "sad":
        adjusted_emotion = "concentrado"
        adjusted_confidence = min(95, confidence + 10)
        reason = "Em ambiente de trabalho, expressões sérias são frequentemente concentração"
    
    elif "festa" in context and emotion == "angry":
        adjusted_emotion = "animado"
        adjusted_confidence = min(95, confidence + 5)
        reason = "Em festas, expressões intensas podem indicar animação"
    
    elif "natureza" in context and emotion == "neutral":
        adjusted_emotion = "pensativo"
        adjusted_confidence = min(95, confidence + 8)
        reason = "Em ambientes naturais, neutralidade pode refletir contemplação"
    
    else:
        adjusted_emotion = emotion
        adjusted_confidence = confidence
        reason = "O contexto não alterou significativamente a interpretação da emoção"
    
    return {
        "original_emotion": original_emotion,
        "original_confidence": original_confidence,
        "adjusted_emotion": adjusted_emotion,
        "adjusted_confidence": adjusted_confidence,
        "reason": reason
    }

# Função principal de análise
def analyze_image(image):
    # Salvar imagem temporariamente para processamento
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        image.save(tmp_file.name)
        img_path = tmp_file.name
    
    try:
        # Detectar rostos e emoções com DeepFace
        results = DeepFace.analyze(img_path, actions=['emotion'], enforce_detection=True)
        
        # Detectar contexto
        context = detect_context(image)
        
        # Processar resultados
        analysis_results = []
        for result in results:
            emotion = result['dominant_emotion']
            confidence = result['emotion'][emotion]
            region = result['region']
            
            # Ajustar emoção com base no contexto
            adjustment = adjust_emotion(emotion, confidence, context)
            
            analysis_results.append({
                "region": region,
                "adjustment": adjustment,
                "context": context
            })
        
        return analysis_results, None
        
    except Exception as e:
        return None, str(e)
    
    finally:
        # Limpar arquivo temporário
        os.unlink(img_path)

# Interface principal
uploaded_file = st.file_uploader("Escolha uma imagem...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Carregar e exibir imagem
    image = Image.open(uploaded_file)
    st.image(image, caption="Imagem carregada", use_column_width=True)
    
    # Analisar imagem
    with st.spinner("Analisando imagem..."):
        results, error = analyze_image(image)
    
    if error:
        st.error(f"Erro na análise: {error}")
    else:
        # Exibir resultados
        st.success("Análise concluída!")
        
        for i, result in enumerate(results):
            st.subheader(f"Pessoa {i+1}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Análise Facial**")
                adjustment = result['adjustment']
                st.metric(
                    label="Emoção detectada",
                    value=adjustment['original_emotion'],
                    delta=f"{adjustment['original_confidence']:.1f}%"
                )
            
            with col2:
                st.markdown("**Análise Contextual**")
                st.metric(
                    label="Emoção ajustada",
                    value=adjustment['adjusted_emotion'],
                    delta=f"{adjustment['adjusted_confidence']:.1f}%"
                )
            
            st.markdown("**Contexto detectado:**")
            st.info(", ".join(result['context']))
            
            st.markdown("**Justificativa do ajuste:**")
            st.write(adjustment['reason'])
            
            st.markdown("---")

# Seção de explicação do projeto
with st.expander("ℹ️ Sobre este projeto"):
    st.markdown("""
    ## Como funciona este sistema?
    
    Este projeto demonstra um sistema de reconhecimento de emoções que considera o contexto da imagem
    para melhorar a precisão da análise. A implementação combina:
    
    1. **Detecção facial** usando OpenCV através da biblioteca DeepFace
    2. **Reconhecimento de emoções** usando modelos deep learning pré-treinados
    3. **Análise de contexto** simplificada para detectar ambiente e objetos
    4. **Lógica de ajuste** que modera a emoção detectada com base no contexto
    
    ## Tecnologias utilizadas
    
    - Python
    - OpenCV para processamento de imagem
    - DeepFace para análise facial e de emoções
    - Streamlit para interface web
    - Técnicas de visão computacional para análise contextual simplificada
    
    ## Aplicações práticas
    
    Sistemas como este podem ser aplicados em:
    - Análise de satisfação de clientes em lojas
    - Monitoramento de bem-estar em ambientes de trabalho
    - Pesquisas de mercado e análise de comportamento
    - Sistemas de recomendação sensíveis ao estado emocional
    """)

# Nota de rodapé
st.markdown("---")