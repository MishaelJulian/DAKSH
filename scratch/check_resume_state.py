import json
import os
import glob

def check_state():
    base_dir = r"C:\Users\misha\OneDrive\Desktop\daksh\eCourts_Executive_Petitions_2023"
    cases_path = os.path.join(base_dir, "cases.json")
    checkpoint_path = os.path.join(base_dir, "checkpoint_2023.json")
    snapshots_dir = os.path.join(base_dir, "snapshots")
    orders_dir = os.path.join(base_dir, "orders")
    
    # 1. Load cases.json
    try:
        with open(cases_path, "r", encoding="utf-8") as f:
            cases = json.load(f)
            cases_count = len(cases)
    except Exception as e:
        cases = []
        cases_count = f"Error: {e}"
        
    # 2. Load checkpoint_2023.json
    try:
        with open(checkpoint_path, "r", encoding="utf-8") as f:
            checkpoint = json.load(f)
    except Exception as e:
        checkpoint = {}
        
    completed_cnrs_in_checkpoint = checkpoint.get("completed_cnrs", [])
    cases_processed_in_checkpoint = checkpoint.get("cases_processed", 0)
    last_completed_case = checkpoint.get("last_completed_case", None)
    last_completed_cnr = checkpoint.get("last_completed_cnr", None)
    last_page = checkpoint.get("last_page", None)
    
    # 3. Snapshots
    snapshot_files = glob.glob(os.path.join(snapshots_dir, "*"))
    snapshots_count = len(snapshot_files)
    
    # 4. Orders
    order_files = glob.glob(os.path.join(orders_dir, "*"))
    orders_count = len(order_files)

    # 5. History rows count in cases
    total_history_rows = 0
    total_purpose_of_hearing = 0
    for case in cases:
        # Check metadata/history
        history = case.get("extra_metadata", {}).get("history", []) if isinstance(case.get("extra_metadata"), dict) else []
        if not history and isinstance(case.get("extra_metadata"), str):
            try:
                meta = json.loads(case["extra_metadata"])
                history = meta.get("history", [])
            except:
                pass
        total_history_rows += len(history)
        for h in history:
            if h.get("purpose_of_hearing") or h.get("purpose"):
                total_purpose_of_hearing += 1

    print(f"Cases count in cases.json: {cases_count}")
    print(f"Checkpoint cases processed count: {cases_processed_in_checkpoint}")
    print(f"Checkpoint completed_cnrs length: {len(completed_cnrs_in_checkpoint)}")
    print(f"Last completed case: {last_completed_case}")
    print(f"Last completed CNR: {last_completed_cnr}")
    print(f"Last page: {last_page}")
    print(f"Snapshots count: {snapshots_count}")
    print(f"Orders count (folder): {orders_count}")
    print(f"Total history rows: {total_history_rows}")
    print(f"Total purpose_of_hearing values: {total_purpose_of_hearing}")

if __name__ == "__main__":
    check_state()
