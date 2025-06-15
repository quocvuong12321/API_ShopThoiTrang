import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms
from transformers import ViTModel

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# --- ViT Embedding Model ---
class ViTEmbeddingModel(nn.Module):
    def __init__(self, vit, embedding_dim=128):
        super(ViTEmbeddingModel, self).__init__()
        self.vit = vit
        self.embedding = nn.Linear(vit.config.hidden_size, embedding_dim)

    def forward(self, x):
        outputs = self.vit(pixel_values=x)
        pooled_output = outputs.pooler_output
        return self.embedding(pooled_output)

# --- Khởi tạo model & load weights ---
vit_backbone = ViTModel.from_pretrained("google/vit-base-patch16-224-in21k")
model = ViTEmbeddingModel(vit=vit_backbone, embedding_dim=128).to(device)
model_path = os.path.join(os.path.dirname(__file__), '..', 'save_models', 'ViT_best_model.pth')
model_path = os.path.abspath(model_path)
model.load_state_dict(torch.load(model_path, map_location=device))
model.eval()

# --- Transform ảnh ---
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5]*3, std=[0.5]*3),
])

# --- Hàm trích xuất embedding ảnh ---
def get_embedding(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
        img_tensor = transform(img).unsqueeze(0).to(device)
        img.close()
    except Exception as e:
        # print(f"Lỗi mở ảnh: {image_path}, {e}")
        return None

    with torch.no_grad():
        emb = model(img_tensor)
        emb = F.normalize(emb, p=2, dim=1)

    return emb.squeeze(0)

# --- Load database embedding ---
embedding_path = os.path.join(os.path.dirname(__file__), '..', 'embedding_data')
embedding_path = os.path.abspath(embedding_path)
def load_embedding_database(save_path=embedding_path):
    embeddings = torch.load(os.path.join(save_path, "ViT_embeddings.pt"), map_location=device)
    with open(os.path.join(save_path, "image_paths.txt"), "r", encoding="utf-8") as f:
        image_paths = [line.strip() for line in f.readlines()]

    return embeddings, image_paths

def search_top_k_return_ids(query_image_path, top_k=100, similarity_threshold=0.8):
    embeddings, image_paths = load_embedding_database()

    query_emb = get_embedding(query_image_path)
    if query_emb is None:
        return []

    similarities = F.cosine_similarity(query_emb.unsqueeze(0), embeddings)

    # Lọc theo threshold
    filtered = [(i, similarities[i].item()) for i in range(len(similarities)) if similarities[i] > similarity_threshold]

    # Sắp xếp theo similarity giảm dần và lấy top_k
    filtered_sorted = sorted(filtered, key=lambda x: x[1], reverse=True)[:top_k]

    result = []
    for idx, score in filtered_sorted:
        filename = os.path.basename(image_paths[idx])
        product_spu_id = os.path.splitext(filename)[0].split("_")[0]
        result.append({
            'product_spu_id': product_spu_id,
            'score': score
        })

    return result