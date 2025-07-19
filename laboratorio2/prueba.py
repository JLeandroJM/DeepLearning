import os
import nibabel as nib
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class BrainDataset(Dataset):
    def __init__(self,rootpath,transform=None):
        self.transform = transform
        self.samples = [os.path.join(rootpath,r) for r in os.listdir(rootpath) if os.path.isdir(os.path.join(rootpath,r))]

    def __len__(self):
        return len(self.samples)

    def loadTensor(self,filepath):
        img = nib.load(filepath).get_fdata()
        tensor = torch.tensor(img, dtype=torch.float32).permute(2,0,1) # [H,W,D]  -> [D,H,W] 
        return tensor[:154]

    def __getitem__(self,idx):
        folder = self.samples[idx]

        flair = seg = t1 = t1ce = t2 = None
        for file in os.listdir(folder):
            mode = file.split("_")[-1]
            filepath = os.path.join(folder, file)
            if mode == "flair.nii.gz":
                flair = self.loadTensor(filepath)
            elif mode == "seg.nii.gz":
                seg = self.loadTensor(filepath)
            elif mode == "t1.nii.gz":
                t1 = self.loadTensor(filepath)
            elif mode == "t1ce.nii.gz":
                t1ce = self.loadTensor(filepath)
            elif mode == "t2.nii.gz":
                t2 = self.loadTensor(filepath)
        voxel = torch.stack([flair,t1,t1ce,t2],dim=0)   # [chan,D,H,W]

        # 0 -> Fondo
        # 1,2,4 -> tumor
        
        #         0 1 2 3
        # Net -> [0 1 0 0]
        seg[seg==4] = 3
        seg = seg.long()
        return (voxel,seg)

def DoubleConv3d(in_chan, out_chan):
    return nn.Sequential(
        nn.Conv3d(in_chan, out_chan, kernel_size=3, padding=1),
        nn.ReLU(inplace=True),
        nn.Conv3d(out_chan, out_chan, kernel_size=3, padding=1),
        nn.ReLU(inplace=True),
    )

class Unet3D(nn.Module):
    def __init__(self, n_chan, n_classes):
        super(Unet3D, self).__init__()

        # Encoder
        self.enc1 = DoubleConv3d(n_chan, 32)
        self.pool1 = nn.MaxPool3d(kernel_size=2, stride=2)

        self.enc2 = DoubleConv3d(32, 64)
        self.pool2 = nn.MaxPool3d(kernel_size=2, stride=2)

        # Bottleneck
        self.bottleneck = DoubleConv3d(64, 128)

        # Decoder
        self.up2 = nn.ConvTranspose3d(128, 64, kernel_size=2, stride=2, output_padding=(1,0,0))
        self.dec2 = DoubleConv3d(128, 64)

        self.up1 = nn.ConvTranspose3d(64, 32, kernel_size=2, stride=2)
        self.dec1 = DoubleConv3d(64, 32)

        # Output
        self.OutLayer = nn.Conv3d(32, n_classes, kernel_size=1)

    def forward(self, x):
        z1 = self.enc1(x)
        z2 = self.pool1(z1)

        z2 = self.enc2(z2)
        Z = self.pool2(z2)

        Z = self.bottleneck(Z)
        print("up1")
        y = self.up2(Z)
        y = torch.cat([y, z2], dim=1)
        y = self.dec2(y)
        print("up2")
        y = self.up1(y)
        y = torch.cat([y, z1], dim=1)
        y = self.dec1(y)
        print("ultimo")
        return self.OutLayer(y)
    
root = "BrainTrain"

dataset = BrainDataset(root)

# print(len(dataset)) : 1000
# grupo, seg = dataset[0]
# print(seg.shape) : [154,240,240]
# print(grupo.shape) : [4,154,240,240]

n_dataset = len(dataset)
n_train   = int(0.75 * n_dataset)
n_eval    = n_dataset - n_train

trainSubset, evalSubset = random_split(dataset, [n_train, n_eval],
    generator=torch.Generator().manual_seed(21)
)
trainLoader = DataLoader(trainSubset,batch_size=1, shuffle=True)
evalLoader  = DataLoader( evalSubset,batch_size=1, shuffle=False)

model = Unet3D(n_chan=4, n_classes=4).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

num_epochs = 10
for epoch in range(num_epochs):
    model.train()
    total_loss = 0
    
    for inputs, labels in trainLoader:
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)  # (batch, 4, D, H, W)
        print("elemento procesado")
        loss = criterion(outputs, labels)  # CE espera (batch, clases, D, H, W) y (batch, D, H, W)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()

    print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {total_loss/len(trainLoader):.4f}")

model.eval()
eval_loss = 0
with torch.no_grad():
    for inputs, labels in evalLoader:
        inputs, labels = inputs.to(device), labels.to(device)
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        eval_loss += loss.item()
    avg_eval_loss = eval_loss / len(evalLoader)
print(f"Eval Loss: {avg_eval_loss:.4f}")

torch.save(model.state_dict(), "model_seg.pth")