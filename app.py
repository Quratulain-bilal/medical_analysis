import streamlit as st
from PIL import Image
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import urllib.request
import base64

# UI Configuration
st.set_page_config(
    page_title="TraumaScan Pro",
    page_icon="🩹",
    layout="centered"  # Center the entire app layout
)

# Security setup
API_KEY = 'AIzaSyBWoYAmrL9tOes0yoUOiFk6dAlcwBavEYA'  # Replace with your actual API key
genai.configure(api_key=API_KEY)

# Medical model configuration
model = genai.GenerativeModel(
    'gemini-1.5-pro',
    generation_config={
        "temperature": 0.9,  # Adjust for creativity
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,  # Adjust for response length
    }
)

# Custom CSS for modern and attractive UI
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

body {
    font-family: 'Poppins', sans-serif;
    background: linear-gradient(135deg, #f0f2f5, #e6f7ff); /* Light gradient background */
    color: #333;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    margin: 0;
    padding: 20px;
}

.container {
    max-width: 1200px;
    width: 100%;
    margin: 0 auto;
    padding: 20px;
}

.medical-header {
    background: linear-gradient(135deg, #007BFF, #00BFFF);
    padding: 40px 20px;
    border-radius: 15px;
    margin-bottom: 30px;
    text-align: center;
    color: white;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.medical-header h1 {
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 10px;
}

.medical-header p {
    font-size: 20px;
    font-weight: 400;
}

.uploader {
    background: white;
    padding: 25px;
    border-radius: 15px;
    margin: 20px 0;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    text-align: center;
}

.medical-report {
    background: white;
    border-radius: 15px;
    padding: 25px;
    margin: 20px 0;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.section-header {
    color: #007BFF;
    font-size: 28px;
    font-weight: 600;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.section-header i {
    margin-right: 10px;
}

.detail-box {
    background: #f8f9fa;
    border-left: 5px solid #007BFF;
    padding: 20px;
    margin: 15px 0;
    border-radius: 10px;
    font-size: 16px;
    line-height: 1.6;
}

.medical-disclaimer {
    background: #ffeeba;
    color: #856404;
    padding: 20px;
    border-radius: 10px;
    margin: 20px 0;
    font-size: 16px;
    text-align: center;
}

.footer {
    text-align: center;
    color: #6c757d;
    margin: 20px;
    font-size: 14px;
}

/* Center the image */
.image-container {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 20px 0;
}

.image-container img {
    max-width: 100%;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}
</style>
""", unsafe_allow_html=True)

def analyze_injury(image):
    """Clinical image analysis pipeline"""
    try:
        prompt = """
        Analyze this clinical image and provide:
        1. Primary diagnosis (burn, fracture, laceration, etc)
        2. Anatomical location (left forearm, right knee, etc)
        3. Severity scale (1-5)
        4. Immediate treatment steps
        5. Follow-up recommendations
        6. Precautions to take
        7. Recommended medicines
        
        Return in strict medical format:
        DX: 
        SEVERITY: 
        TX: 
        PRECAUTIONS: 
        MEDICINES: 
        """
        
        # Configure safety settings
        safety_config = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

        response = model.generate_content(
            [prompt, image],
            safety_settings=safety_config,
            stream=False
        )
        
        return response.text.strip()
    
    except Exception as e:
        return f"CLINICAL ERROR: {str(e)}"

def extract_section(result, section_name):
    """Extract the complete section from the result"""
    if f"{section_name}:" in result:
        start_index = result.index(f"{section_name}:") + len(f"{section_name}:")
        end_index = result.find("\n\n", start_index)  # Look for the next empty line
        if end_index == -1:  # If no empty line is found, take the rest of the text
            end_index = len(result)
        return result[start_index:end_index].strip()
    return ""

# Main container
st.markdown('<div class="container">', unsafe_allow_html=True)

# Medical-themed header
st.markdown("""
<div class="medical-header">
    <h1><i class="fas fa-stethoscope"></i> TraumaScan Pro</h1>
    <p>AI-Powered Clinical Image Analysis</p>
</div>
""", unsafe_allow_html=True)

# Image uploader with medical styling
st.markdown('<div class="uploader">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("UPLOAD MEDICAL IMAGE", 
                                type=['png', 'jpg', 'jpeg'],
                                accept_multiple_files=False,
                                help="Supported formats: PNG, JPG, JPEG")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file:
    image = Image.open(uploaded_file)
    
    # Image display with analysis
    st.markdown('<div class="image-container">', unsafe_allow_html=True)
    st.image(image, caption="Clinical Image Analysis", width=400)
    st.markdown('</div>', unsafe_allow_html=True)
        
    with st.spinner("Performing clinical analysis..."):
        result = analyze_injury(image)
            
    # Medical report display
    st.markdown('<div class="medical-report">', unsafe_allow_html=True)
        
    # Diagnosis Section
    st.markdown('<div class="section-header"><i class="fas fa-diagnoses"></i> DIAGNOSIS</div>', unsafe_allow_html=True)
    diagnosis = extract_section(result, "DX")
    st.markdown(f'<div class="detail-box">{diagnosis}</div>', unsafe_allow_html=True)
        
    # Treatment Section
    st.markdown('<div class="section-header"><i class="fas fa-capsules"></i> TREATMENT</div>', unsafe_allow_html=True)
    treatment = extract_section(result, "TX")
    st.markdown(f'<div class="detail-box">{treatment}</div>', unsafe_allow_html=True)
        
    # Precautions Section
    st.markdown('<div class="section-header"><i class="fas fa-shield-alt"></i> PRECAUTIONS</div>', unsafe_allow_html=True)
    precautions = extract_section(result, "PRECAUTIONS")
    st.markdown(f'<div class="detail-box">{precautions}</div>', unsafe_allow_html=True)
        
    # Medicines Section
    st.markdown('<div class="section-header"><i class="fas fa-pills"></i> MEDICINES</div>', unsafe_allow_html=True)
    medicines = extract_section(result, "MEDICINES")
    st.markdown(f'<div class="detail-box">{medicines}</div>', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
        
    # Medical disclaimer
    st.markdown('<div class="medical-disclaimer"><i class="fas fa-info-circle"></i> This is not a substitute for professional medical advice. Consult a licensed physician for confirmation.</div>', unsafe_allow_html=True)

# Footer
st.markdown('<div class="footer">Developed with ❤️ by Medical AI Research Group</div>', unsafe_allow_html=True)

# Close container
st.markdown('</div>', unsafe_allow_html=True)
