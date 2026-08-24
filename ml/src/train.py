from __future__ import annotations
import argparse, copy, json, os, random
from pathlib import Path
import numpy as np, torch
from sklearn.metrics import f1_score
from torch import nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.models import EfficientNet_V2_S_Weights, efficientnet_v2_s
def seed_all(seed): random.seed(seed); np.random.seed(seed); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
def make_tf(size):
    w=EfficientNet_V2_S_Weights.DEFAULT; norm=transforms.Normalize(mean=w.transforms().mean,std=w.transforms().std); return transforms.Compose([transforms.RandomResizedCrop(size,scale=(0.82,1.0)),transforms.RandomHorizontalFlip(),transforms.RandomRotation(10),transforms.ColorJitter(0.15,0.15,0.10,0.02),transforms.ToTensor(),norm]), transforms.Compose([transforms.Resize(int(size*1.14)),transforms.CenterCrop(size),transforms.ToTensor(),norm])
def epoch(model,loader,criterion,device,optimizer=None,scaler=None):
    training=optimizer is not None; model.train(training); losses=[]; yt=[]; yp=[]
    for x,y in loader:
        x,y=x.to(device),y.to(device)
        if training: optimizer.zero_grad(set_to_none=True)
        amp=scaler is not None and device.type=="cuda"
        with torch.autocast(device_type=device.type,enabled=amp): logits=model(x); loss=criterion(logits,y)
        if training:
            if amp: scaler.scale(loss).backward(); scaler.step(optimizer); scaler.update()
            else: loss.backward(); optimizer.step()
        losses.append(float(loss.detach().cpu())); yt.extend(y.detach().cpu().tolist()); yp.extend(logits.argmax(1).detach().cpu().tolist())
    return {"loss":float(np.mean(losses)),"accuracy":float(np.mean(np.asarray(yt)==np.asarray(yp))),"macro_f1":float(f1_score(yt,yp,average="macro",zero_division=0))}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--epochs",type=int,default=25); ap.add_argument("--batch-size",type=int,default=32); ap.add_argument("--learning-rate",type=float,default=3e-4); ap.add_argument("--weight-decay",type=float,default=1e-4); ap.add_argument("--image-size",type=int,default=224); ap.add_argument("--dropout",type=float,default=0.25); ap.add_argument("--patience",type=int,default=6); ap.add_argument("--seed",type=int,default=42); a=ap.parse_args(); seed_all(a.seed)
    model_dir=Path(os.getenv("SM_MODEL_DIR","/opt/ml/model")); model_dir.mkdir(parents=True,exist_ok=True); train_dir=Path(os.getenv("SM_CHANNEL_TRAIN","/opt/ml/input/data/train")); val_dir=Path(os.getenv("SM_CHANNEL_VAL","/opt/ml/input/data/val")); tr_tf,ev_tf=make_tf(a.image_size); tr_ds=datasets.ImageFolder(train_dir,transform=tr_tf); va_ds=datasets.ImageFolder(val_dir,transform=ev_tf)
    if tr_ds.class_to_idx!=va_ds.class_to_idx: raise RuntimeError("Class mapping mismatch.")
    workers=min(8,os.cpu_count() or 2); tr_ld=DataLoader(tr_ds,batch_size=a.batch_size,shuffle=True,num_workers=workers,pin_memory=True); va_ld=DataLoader(va_ds,batch_size=a.batch_size,shuffle=False,num_workers=workers,pin_memory=True); device=torch.device("cuda" if torch.cuda.is_available() else "cpu"); model=efficientnet_v2_s(weights=EfficientNet_V2_S_Weights.DEFAULT); n=model.classifier[-1].in_features; model.classifier=nn.Sequential(nn.Dropout(a.dropout),nn.Linear(n,len(tr_ds.classes))); model.to(device); criterion=nn.CrossEntropyLoss(label_smoothing=0.05); opt=AdamW(model.parameters(),lr=a.learning_rate,weight_decay=a.weight_decay); sched=CosineAnnealingLR(opt,T_max=a.epochs); scaler=torch.cuda.amp.GradScaler(enabled=device.type=="cuda"); best=-1.0; best_state=copy.deepcopy(model.state_dict()); bad=0; hist=[]
    for e in range(1,a.epochs+1):
        tr=epoch(model,tr_ld,criterion,device,opt,scaler); va=epoch(model,va_ld,criterion,device); sched.step(); hist.append({"epoch":e,"train":tr,"validation":va}); print(f"epoch={e} train_f1={tr['macro_f1']:.4f} val_f1={va['macro_f1']:.4f}")
        if va["macro_f1"]>best: best=va["macro_f1"]; best_state=copy.deepcopy(model.state_dict()); bad=0
        else:
            bad+=1
            if bad>=a.patience: break
    model.load_state_dict(best_state); torch.save({"model_state":model.state_dict(),"class_names":tr_ds.classes,"image_size":a.image_size,"dropout":a.dropout,"architecture":"efficientnet_v2_s","validation_macro_f1":best},model_dir/"model.pt"); (model_dir/"training_history.json").write_text(json.dumps(hist,indent=2)); print(f"best_validation_macro_f1={best:.6f}")
if __name__=="__main__": main()
