from __future__ import annotations
import argparse, os
from pathlib import Path
from huggingface_hub import HfApi

def main():
    p=argparse.ArgumentParser(); p.add_argument('--repo-id',required=True); p.add_argument('--folder',type=Path,required=True); a=p.parse_args()
    if not a.repo_id.startswith('singhankit491/'): raise ValueError('Destination must be under singhankit491')
    for name in ('README.md','index.html'):
        if not (a.folder/name).is_file(): raise FileNotFoundError(name)
    token=os.getenv('HF_TOKEN')
    if not token: raise ValueError('HF_TOKEN is required')
    api=HfApi(token=token)
    if api.whoami()['name']!='singhankit491': raise ValueError('Authenticated Hugging Face account mismatch')
    api.create_repo(repo_id=a.repo_id,repo_type='space',space_sdk='static',exist_ok=True,private=False)
    commit=api.upload_folder(repo_id=a.repo_id,repo_type='space',folder_path=a.folder,commit_message='Deploy validated OtoSage static portfolio Space')
    info=api.space_info(a.repo_id,files_metadata=False)
    print('Published:',commit.commit_url); print('Revision:',info.sha)
if __name__=='__main__': main()
