import pandas as pd
import nltk
import joblib
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score

# Download stopwords
nltk.download('stopwords')
from nltk.corpus import stopwords

# Load dataset with correct encoding
data = pd.read_csv("dataset/spam.csv", encoding="latin-1")

# Keep only first two columns (label, message)
data = data.iloc[:, :2]
data.columns = ["label", "message"]

# Text cleaning function
def clean_text(text):
    text = text.lower()
    text = re.sub(r'http\S+', '', text)      # remove links
    text = re.sub(r'[^a-zA-Z ]', '', text)  # remove symbols
    return text

# Apply cleaning
data['message'] = data['message'].apply(clean_text)

# Convert labels: spam -> 1, ham -> 0
data['label'] = data['label'].map({'spam': 1, 'ham': 0})

# Features and target
X = data['message']
y = data['label']

# Convert text to numbers
vectorizer = TfidfVectorizer(stop_words=stopwords.words('english'))
X_vec = vectorizer.fit_transform(X)

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X_vec, y, test_size=0.2, random_state=42
)

# Train model
model = MultinomialNB()
model.fit(X_train, y_train)

# Test model
pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, pred))

# Save model and vectorizer
joblib.dump(model, "model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

print("Model and Vectorizer saved successfully!")
