import streamlit as st
import json
import re
import time
import datetime
import google.generativeai as genai
import requests
import PyPDF2
import io
import docx

# Set page configuration
st.set_page_config(
    page_title="PowerPoint Content Generator",
    page_icon="📊",
    layout="wide"
)

# Model details
model_name = "gemini-1.5-flash-001"
api_key = "AIzaSyA1GTDcjUfz8wYaGJpxCKtgKdmCZb95XXI"
API_URL_Midjourney = "https://api-inference.huggingface.co/models/Jovie/Midjourney"
headers = {"Authorization": "Bearer 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"}

def extract_text_from_pdf(file_bytes):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return None

def extract_text_from_docx(file_bytes):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error extracting text from DOCX: {str(e)}")
        return None

def extract_text_from_txt(file_bytes):
    """Extract text from TXT file"""
    try:
        return file_bytes.decode('utf-8').strip()
    except Exception as e:
        st.error(f"Error extracting text from TXT: {str(e)}")
        return None

def extract_text_from_file(uploaded_file):
    """Extract text based on file type"""
    try:
        file_bytes = uploaded_file.read()
        file_type = uploaded_file.type
        
        if file_type == "application/pdf":
            return extract_text_from_pdf(file_bytes)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return extract_text_from_docx(file_bytes)
        elif file_type == "text/plain":
            return extract_text_from_txt(file_bytes)
        else:
            st.error("Unsupported file type. Please upload a PDF, DOCX, or TXT file.")
            return None
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None
def query_midjourney(payload):
    """Make a request to the Midjourney API"""
    response = requests.post(API_URL_Midjourney, headers=headers, json=payload)
    return response

def generate_image_for_example(example_text: str) -> bytes:
    """Generate an educational and visually engaging image based on the example text."""
    
    # Create an enhanced prompt for generating a highly relevant and engaging educational image
    refinement_prompt = f"""
    Generate a **high-quality, detailed, and engaging image** designed for teaching students in a PowerPoint presentation.

    **Image Context & Theme:**
    - The image should be highly **educational**, visually appealing, and directly relevant to the following text: **"{example_text}"**.
    - It should use a **student-friendly** visual style that simplifies complex concepts while keeping the imagery engaging.
    - The design should be **clear, well-structured, and informative**, ensuring the message is easily understood by students of different learning levels.

    **Key Requirements:**
    - **No unnecessary text** on the image; the visual should communicate the concept clearly.
    - If necessary, integrate **infographics, flowcharts, labeled diagrams, or conceptual illustrations** that enhance understanding.
    - Use a **human-centric approach** (if applicable) or **technological themes** to make abstract concepts relatable.
    - The image should **align with the teaching topic** and be suitable for a PowerPoint slide.

    **Additional Notes for Refinement:**
    - Ensure **sharp details, vibrant colors, and high contrast** for maximum visibility in a presentation.
    - Avoid excessive artistic clutter; maintain **a clear focal point**.
    - The image should **naturally guide the student's attention** to the key takeaway.
    - Use **real-world analogies, simplified diagrams, or storytelling elements** where applicable.
    """
    
    refined_completion = llm.generate_content([refinement_prompt])
    refined_prompt = refined_completion.text.strip()
    
    if refined_prompt:
        refined_prompt =  refined_prompt
        response = query_midjourney({"inputs": refined_prompt})
        if response.status_code == 200:
            return response.content
    return None
# Initialize Gemini
genai.configure(api_key=api_key)
llm = genai.GenerativeModel(model_name=model_name)

def process_content(topic_description: str) -> dict:
    """Process the topic and generate PowerPoint content using Gemini."""
    prompt = f"""
Create a detailed PowerPoint presentation for the topic: "{topic_description}". The presentation should be structured with the following sections, and each section should contain detailed content that can be used directly on PowerPoint slides.

Provide content for the following sections:
1. **Introduction**:
    - A comprehensive introduction to the topic. Define the topic in detail and explain its importance. Include background information that would be useful for an educational audience.

2. **Main Content**:
    - Break the topic down into multiple key concepts or subtopics. For each subtopic:
        - Detailed explanation: Expand on the concept with technical details where applicable.
        - Include examples that make the concept easier to understand.
        - Mention real-world applications, visuals (e.g., charts, diagrams, or pictures), and any key points that would be useful for the audience to grasp the concept.

3. **Interactive Activity**:
    - Suggest an interactive activity that engages the audience, including instructions, materials needed, and discussion prompts.

4. **Conclusion**:
    - Summarize the key takeaways from the presentation.
    - Provide a conclusion that reinforces the importance of the topic and how it relates to real-world scenarios.
    - Suggest questions for discussion or reflection.

5. **References/Additional Information**:
    - Suggest a list of sources, additional reading, or references that the audience can explore to learn more about the topic.

Output the detailed content for the above sections in a clear, structured format, suitable for use in a PowerPoint presentation. Include enough depth in each section to allow for a complete presentation without the need for further elaboration.

Output the content in the following format:

{{
  "Introduction": {{
    "Title": "Introduction to {topic_description}",
    "Content": "Detailed explanation, definitions, and importance of the topic."
  }},
  "Main Content": {{
    "Subtopic 1": {{
      "Title": "Title of Subtopic 1",
      "Explanation": "Expanded explanation of Subtopic 1 with technical depth.",
      "Examples": "Real-world examples or visuals that can be included.",
      "Key Takeaways": "Summary of the key points to be highlighted."
    }},
    "Subtopic 2": {{
      "Title": "Title of Subtopic 2",
      "Explanation": "Detailed explanation of Subtopic 2.",
      "Examples": "Real-world examples or visuals.",
      "Key Takeaways": "Summary of the key points."
    }}
  }},
  "Interactive Activity": {{
    "Title": "Interactive Activity on {topic_description}",
    "Instructions": "Step-by-step instructions for the activity.",
    "Materials Needed": "List of materials or resources needed.",
    "Discussion Prompts": "Prompts for group discussion or reflection."
  }},
  "Conclusion": {{
    "Summary": "Summary of the main points discussed in the presentation.",
    "Real-world Application": "How the topic applies to real-world situations.",
    "Discussion Questions": "Thought-provoking questions for the audience."
  }},
  "References": {{
    "Suggested Readings": "Books, articles, or websites for further learning.",
    "Additional Resources": "Additional materials to deepen knowledge on the topic."
  }}
}}
"""

    try:
        completion = llm.generate_content(prompt, generation_config={'temperature': 0})
        response = completion.text

        if not response.strip():
            raise ValueError("Empty response from the model.")

        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            response = json_match.group().strip()
        else:
            raise ValueError("No structured outline found in the response.")

        parsed_response = json.loads(response)
        return parsed_response

    except (json.JSONDecodeError, AttributeError, ValueError) as e:
        st.error(f"Error processing content: {str(e)}")
        return {"error": f"The generated content is not valid. Error: {str(e)}"}

def main():
    st.title("PowerPoint Content Generator with Images 📊")
    st.write("Generate detailed PowerPoint presentation content with example visualizations!")

     # File uploader
    uploaded_file = st.file_uploader(
        "Choose a file", 
        type=["pdf", "docx", "txt"],
        help="Upload a PDF, DOCX, or TXT file containing the content you want to create a presentation for."
    )


    if uploaded_file is not None:
        # Extract text from the file
        with st.spinner("Extracting text from file..."):
            extracted_text = extract_text_from_file(uploaded_file)
            
            if extracted_text:
                st.success("Text extracted successfully!")
                
                # Show extracted text in an expander
                with st.expander("View Extracted Text"):
                    st.text_area("Extracted Content", extracted_text, height=200)
                
                if st.button("Generate Presentation"):
                    with st.spinner("Generating content and images... Please wait."):
                        start_time = time.time()
                        response_data = process_content(extracted_text)
                        
                        if "error" not in response_data:
                            # Create main tabs
                            tabs = st.tabs(["Introduction", "Main Content & Examples", "Interactive Activity", "Conclusion", "References"])
                            
                            # Introduction Tab
                            with tabs[0]:
                                col1, col2 = st.columns([3, 2])
                                with col1:
                                    st.header("Introduction")
                                    intro = response_data["Introduction"]
                                    st.subheader(intro["Title"])
                                    st.write(intro["Content"])

                                with col2:
                                    with st.spinner("Generating visualization for Introduction..."):
                                        intro_image = generate_image_for_example(intro["Content"])
                                    if intro_image:
                                        st.image(intro_image, caption="Visual Representation of Introduction")
                                    else:
                                        st.warning("Could not generate visualization for the introduction.")
                            # Main Content Tab with Examples and Images
                            with tabs[1]:
                                st.header("Main Content")
                                main_content = response_data["Main Content"]
                                
                                for subtopic, content in main_content.items():
                                    with st.expander(content["Title"]):
                                        col3, col4 = st.columns([3, 2])
                                        
                                        with col3:
                                            st.write("**Explanation:**")
                                            st.write(content["Explanation"])
                                            st.write("**Examples:**")
                                            st.write(content["Examples"])
                                            st.write("**Key Takeaways:**")
                                            st.write(content["Key Takeaways"])
                                        
                                        with col4:
                                            st.write("**Visualizations:**")
                                            with st.spinner("Generating image for example..."):
                                                image_bytes = generate_image_for_example(content["Examples"])
                                                if image_bytes:
                                                    st.image(image_bytes, caption=f"Generated visualization for {content['Title']}")
                                                else:
                                                    st.warning("Could not generate image for this example")
                            
                            # Interactive Activity Tab
                            with tabs[2]:
                                st.header("Interactive Activity")
                                activity = response_data["Interactive Activity"]
                                st.subheader(activity["Title"])
                                st.write("**Instructions:**")
                                st.write(activity["Instructions"])
                                st.write("**Materials Needed:**")
                                st.write(activity["Materials Needed"])
                                st.write("**Discussion Prompts:**")
                                st.write(activity["Discussion Prompts"])
                            
                            # Conclusion Tab
                            with tabs[3]:
                                st.header("Conclusion")
                                conclusion = response_data["Conclusion"]
                                st.write("**Summary:**")
                                st.write(conclusion["Summary"])
                                st.write("**Real-world Application:**")
                                st.write(conclusion["Real-world Application"])
                                st.write("**Discussion Questions:**")
                                st.write(conclusion["Discussion Questions"])
                            
                            # References Tab
                            with tabs[4]:
                                st.header("References")
                                references = response_data["References"]
                                st.write("**Suggested Readings:**")
                                st.write(references["Suggested Readings"])
                                st.write("**Additional Resources:**")
                                st.write(references["Additional Resources"])
                            
                            end_time = time.time()
                            st.success(f"Content and images generated successfully! (Time taken: {end_time - start_time:.2f} seconds)")
                        else:
                            st.error("Failed to generate content. Please try again.")

if __name__ == "__main__":
    main()
