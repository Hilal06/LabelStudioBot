import pandas as pd
import json
from label_studio_sdk.client import LabelStudio
import sys
import time
import random
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    print("="*50)
    print("🤖 Label Studio Auto-Annotation Bot (FILTER MODE) 🤖")
    print("="*50)

    # Setup konfigurasi
    LABEL_STUDIO_URL = 'https://bdsrc.binus.ac.id/label-studio/'
    API_KEY = os.getenv('LABEL_STUDIO_API_KEY')
    if not API_KEY:
        print("Error: LABEL_STUDIO_API_KEY tidak ditemukan di environment atau file .env")
        sys.exit(1)
    PROJECT_ID = 20
    
    EXCEL_FILE = 'Annotated_Tweets_Cleaned.xlsx'
    ID_FILTER_FILE = 'test_data.json'
    LABEL_COLUMN = 'sentiment'
    
    # Label config defaults
    FROM_NAME = 'sentiment'
    TO_NAME = 'text'

    print(f"\nMenghubungkan ke Label Studio di {LABEL_STUDIO_URL}...")
    ls = LabelStudio(
        base_url=LABEL_STUDIO_URL,
        api_key=API_KEY
    )
    
    print(f"Mengambil daftar task dari Project {PROJECT_ID} untuk mapping ID...")
    try:
        tasks_generator = ls.tasks.list(project=PROJECT_ID)
        all_tasks = list(tasks_generator)
        # Membuat dictionary pemetaan: Data ID (dari excel) -> Internal Task ID (Label Studio)
        id_mapping = {}
        for task in all_tasks:
            data_id = str(task.data.get('id', ''))
            if data_id:
                id_mapping[data_id] = task.id
        print(f"Berhasil memetakan {len(id_mapping)} task dari Label Studio.")
    except Exception as e:
        print(f"Gagal mengambil task dari Label Studio: {e}")
        sys.exit(1)

    # Membaca file ID filter (JSON)
    print(f"\nMembaca file filter ID: {ID_FILTER_FILE}")
    try:
        with open(ID_FILTER_FILE, 'r') as f:
            data = json.load(f)
            
        if isinstance(data, dict) and "dari" in data and "sampai" in data:
            target_ids = list(range(data["dari"], data["sampai"] + 1))
        elif isinstance(data, list):
            target_ids = data
        else:
            raise ValueError("File JSON harus berisi array ID (contoh: [798, 799]) atau object range (contoh: {\"dari\": 800, \"sampai\": 1000})")
            
        print(f"Membatasi eksekusi untuk {len(target_ids)} Data ID (contoh: {target_ids[:5]}{'...' if len(target_ids) > 5 else ''})")
    except Exception as e:
        print(f"Gagal membaca file JSON filter: {e}")
        sys.exit(1)
        
    print(f"Membaca file data Excel: {EXCEL_FILE}")
    try:
        df = pd.read_excel(EXCEL_FILE)
    except Exception as e:
        print(f"Gagal membaca file Excel: {e}")
        sys.exit(1)
        
    print(f"Jumlah total baris di Excel: {len(df)}")
    
    # Memfilter dataframe hanya untuk id yang ada di target_ids
    df_filtered = df[df['id'].isin(target_ids)]
    print(f"Jumlah baris setelah difilter (yang akan diproses): {len(df_filtered)}")
    
    if len(df_filtered) == 0:
        print("Tidak ada ID yang cocok dengan file Excel. Proses dibatalkan.")
        sys.exit(0)
    
    berhasil = 0
    gagal = 0
    
    print("\nMemulai proses anotasi otomatis...")
    for index, row in df_filtered.iterrows():
        excel_id = str(row['id'])
        label_value = row[LABEL_COLUMN]
        
        # Skip jika kosong
        if pd.isna(row['id']) or pd.isna(label_value):
            continue
            
        # Cari internal task ID yang sesungguhnya di Label Studio
        internal_task_id = id_mapping.get(excel_id)
        if not internal_task_id:
            print(f"[-] Gagal: Data ID {excel_id} tidak ditemukan di Project {PROJECT_ID} Label Studio.")
            gagal += 1
            continue

        label_value = str(label_value)
        
        # Format payload anotasi Label Studio
        result_payload = [
            {
                "from_name": FROM_NAME,
                "to_name": TO_NAME,
                "type": "choices",
                "value": {
                    "choices": [label_value]
                }
            }
        ]
        
        try:
            # Mengirimkan anotasi ke internal_task_id
            ls.annotations.create(
                id=internal_task_id, 
                task=internal_task_id,
                result=result_payload
            )
            print(f"[+] Berhasil: Data ID {excel_id} (Internal Task ID {internal_task_id}) -> '{label_value}'")
            berhasil += 1
            
            delay = random.randint(15, 30)
            print(f"Menunggu {delay} detik untuk task berikutnya...")
            time.sleep(delay)
        except Exception as e:
            print(f"[-] Gagal: Data ID {excel_id} -> {e}")
            gagal += 1
            
    print("="*50)
    print(f"🎉 Selesai! Berhasil: {berhasil} task, Gagal: {gagal} task")
    print("="*50)

if __name__ == '__main__':
    main()
