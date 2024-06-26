import streamlit as st
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
import base64
from fpdf import FPDF

class PDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", style="I", size=8)
        self.cell(0, 10, "Created by Health Genie", 0, 0, "C")

def main():
    
    st.title('Health Genie - Disease Prediction')

    # Load the dataset for symptoms
    symptoms_data = pd.read_csv('Testing.csv')

    # Select first 15 symptoms
    selected_features = symptoms_data.columns[1:21]

    # Separate features (X) and target (y)
    X = symptoms_data[selected_features]
    y = symptoms_data['prognosis']

    # Load the dataset for diseases and descriptions
    diseases_data = pd.read_csv('symptom_Description.csv')

    # Create a dictionary mapping diseases to their descriptions
    disease_info = dict(zip(diseases_data['Disease'], diseases_data['Description']))
    
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

    # Train Decision Tree classifier
    clf = DecisionTreeClassifier()
    clf.fit(X_train, y_train)

    # Map symptom severity levels to numerical values
    severity_mapping = {'No': 0, 'Yes': 1,}

    # Get user input
    st.sidebar.header('Select Symptoms for Disease Prediction')
    user_input = {}
    for feature in selected_features:
        severity_level = st.sidebar.selectbox(f'{feature}', ['No', 'Yes'])
        user_input[feature] = severity_mapping[severity_level]

    # Convert user input to DataFrame
    user_data = pd.DataFrame(user_input, index=[0])

    # Predict disease
    if st.sidebar.button('Predict'):
        disease_prediction = clf.predict(user_data)
        predicted_disease = disease_prediction[0]
        
        st.write(f'Predicted Disease: {predicted_disease}')

        # Display additional information about the predicted disease
        if predicted_disease in disease_info:
            st.write('Additional Information:')
            st.write(disease_info[predicted_disease])
        else:
            st.write('Additional information not available.')
        
        st.markdown("""
        **Disclaimer:** This is a machine learning-based model for disease prediction. While it can provide insights, it may not always be accurate. For accurate medical advice, please consult a qualified healthcare professional.
        """)
        
        # Create PDF with predicted output
        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size = 12)
        pdf.cell(200, 10, txt = f"Predicted Disease: {predicted_disease}", ln = True, align = 'C')
        pdf.cell(200, 10, txt = "Additional Information:", ln = True, align = 'L')
        if predicted_disease in disease_info:
            additional_info = disease_info[predicted_disease]
            lines = pdf.multi_cell(0, 10, txt=additional_info)
            total_height = sum(lines)
            if total_height > 275:  # Adjust height to fit on one page
                pdf.add_page()
                pdf.set_font("Arial", size = 12)
                pdf.cell(200, 10, txt = f"Predicted Disease: {predicted_disease}", ln = True, align = 'C')
                pdf.cell(200, 10, txt = "Additional Information:", ln = True, align = 'L')
                pdf.multi_cell(0, 10, txt=additional_info)
        else:
            pdf.multi_cell(0, 10, txt = "Additional information not available.")
        
        pdf.footer()  # Add footer to each page

        # Save PDF
        pdf_output = "predicted_output.pdf"
        pdf.output(pdf_output)

        # Create a download link for the PDF
        with open(pdf_output, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="{pdf_output}">Download Predicted Output</a>'
            st.markdown(href, unsafe_allow_html=True)
        
        
    

if __name__ == "__main__":
    main()
