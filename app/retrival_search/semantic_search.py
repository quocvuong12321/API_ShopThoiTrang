import os
from sentence_transformers import SentenceTransformer
import pandas as pd
import re
from underthesea import text_normalize , word_tokenize
import faiss
# Load model đã fine-tune
from transformers import AutoTokenizer,AutoModelForSequenceClassification
import torch
#load mohinh
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_path = os.path.join(os.path.dirname(__file__), "..","save_models","train_12_5_tapdulieunoitruyvan")
fine_tuned_model = SentenceTransformer(model_path, device="cuda" if torch.cuda.is_available() else "cpu")

MODEL_ID = 'itdainb/PhoRanker'
model_reranking = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)
tokenizer_reranking = AutoTokenizer.from_pretrained(MODEL_ID)

# Đưa mô hình lên GPU nếu có
model_reranking.to(device)

def predict_rank(anchor, search_key):
    """
    Predict ranking score for a pair of anchor and search_key
    """
    # Tokenize inputs
    inputs = tokenizer_reranking(anchor, search_key, 
                       padding=True, 
                       truncation=True, 
                       max_length=256, 
                       return_tensors="pt")
    
    # Đưa inputs lên cùng device với mô hình
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    # Get model predictions
    with torch.no_grad():
        outputs = model_reranking(**inputs)
        scores = torch.sigmoid(outputs.logits).squeeze().cpu().numpy()  # .cpu() để chuyển về CPU nếu cần dùng

    return scores

#ham su ly cau truy van
def clean_text_khacdau(text):
    # Loại bỏ các ký tự đặc biệt và biểu tượng cảm xúc
    text = re.sub(r"[^a-zA-Z0-9\sàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệđìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆĐÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴ]", "", str(text))
    # Loại bỏ khoảng trắng thừa
    text = re.sub(r"\s+", " ", text).strip()
    return text
def split_joined_words(text):
    # text = restore_text(text)
    text = text_normalize(text)
    text= word_tokenize(text,format="text")
    return text
    # Hàm xử lý văn bản
def clean_text_query(text):
    if not isinstance(text, str):
        return ""
    text = clean_text_khacdau(text) 
    text = split_joined_words(text=text)
    return text

#đoc_du_lieu
df_path = os.path.join(os.path.dirname(__file__), "..", "save_models","products_spu.csv")
test_df=pd.read_csv(df_path)
faiss_path = os.path.join(os.path.dirname(__file__), "..", "embedding_data", "faiss_index_train_product_embeddings_train_12_5_tapdulieunoitruyvanc.bin")
index = faiss.read_index(faiss_path)

def search_optimized_12_5(query, top_k=50, page=1, min_similarity=0.8):
    query = clean_text_query(query)
    query_embedding = fine_tuned_model.encode(query, convert_to_tensor=True).cpu().numpy()
    query_embedding = query_embedding.reshape(1, -1)
    faiss.normalize_L2(query_embedding)

    # Tìm kiếm bằng FAISS (gấp 2 top_k * page để đủ kết quả sau khi lọc)
    D, I = index.search(query_embedding, k=2 * top_k * page)

    # Lấy kết quả từ DataFrame
    results = test_df.iloc[I[0]].copy()
    results["faiss_score"] = D[0]

    # Re-ranking bằng predict_rank
    rerank_scores = []
    for _, row in results.iterrows():
        anchor = row["embedding_data"]
        rerank_score = predict_rank(anchor, query)
        rerank_scores.append(rerank_score)
    results["rerank_score"] = rerank_scores

    # Tính điểm trung bình
    results["average_score"] = (results["rerank_score"] + results["faiss_score"]) / 2


    # Sắp xếp và phân trang
    sorted_results = results.sort_values(by="average_score", ascending=False)
    start_idx = (page - 1) * top_k
    end_idx = start_idx + top_k
    paginated_results = sorted_results.iloc[start_idx:end_idx]

    # Trả về danh sách dict như {'product_spu_id': '123', 'score': 0.89}
    return [
        {
            'product_spu_id': str(row["product_spu_id"]),
            'score': float(row["average_score"])
        }
        for _, row in paginated_results.iterrows()
    ]

