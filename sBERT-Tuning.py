from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
import csv

model = SentenceTransformer("all-mpnet-base-v2")

train_examples = []
with open('training_data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        train_examples.append(InputExample(
            texts = [row["sentence1"], row["sentence2"]],
            label = float(row("label"))
        ))

train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
train_loss = losses.CosineSimilarityLoss(model)

# fine-tune to a domain/use-specific dataset
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=1,
    warmup_steps=100,
    output_path="fine_tuned_model"
)